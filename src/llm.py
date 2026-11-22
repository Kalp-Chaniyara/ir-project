"""Loads the local LLM (Llama-3.2-3B-Instruct) and gives three operations:

1. p_no_response(): probability that the first token of the reply is NO-RESPONSE.
   This is the paper's P_nr. Distracting effect (DE) = 1 - P_nr.
2. answer(): a short greedy answer.
3. score_and_answer(): both at once, in a single generation call.

Runs on Apple Silicon (MPS), on an NVIDIA GPU (CUDA) or, slowly, on CPU.
"""
from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.common import NO_RESPONSE, build_messages


def pick_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


class LocalLLM:
    def __init__(self, model_id: str, dtype: str = "float16", device: str | None = None):
        self.device = device or pick_device()
        torch_dtype = getattr(torch, dtype) if self.device != "cpu" else torch.float32
        print(f"Loading {model_id} on {self.device} ({torch_dtype}) ...", flush=True)
        self.tok = AutoTokenizer.from_pretrained(model_id)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch_dtype).to(self.device)
        self.model.eval()
        # Same choice as the paper's code: the first token of "NO-RESPONSE".
        self.no_response_id = self.tok.encode(NO_RESPONSE, add_special_tokens=False)[0]

    # ------------------------------------------------------------------ prompts
    def prompt(self, messages: list[dict]) -> str:
        return self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def _encode(self, prompt: str):
        # The paper tokenizes the chat-template string with the default tokenizer call;
        # we do exactly the same so our P_nr values are comparable with theirs.
        enc = self.tok(prompt, return_tensors="pt")
        return {k: v.to(self.device) for k, v in enc.items()}

    # ------------------------------------------------------------------ operations
    @torch.no_grad()
    def generate(self, prompt: str, max_new_tokens: int, want_first_token_prob: bool = False):
        inputs = self._encode(prompt)
        out = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            pad_token_id=self.tok.pad_token_id,
            return_dict_in_generate=True,
            output_logits=want_first_token_prob,
        )
        new_tokens = out.sequences[0, inputs["input_ids"].shape[1]:]
        text = self.tok.decode(new_tokens, skip_special_tokens=True).strip()
        text = text.split("\n")[0].strip()          # keep the first line only
        p_nr = None
        if want_first_token_prob:
            first_logits = out.logits[0][0].float()   # raw logits for the first generated position
            p_nr = torch.softmax(first_logits, dim=-1)[self.no_response_id].item()
        return text, p_nr

    @torch.no_grad()
    def p_no_response(self, question: str, passage: dict) -> float:
        """Forward pass only, exactly like the paper's compute_no_response_probability()."""
        inputs = self._encode(self.prompt(build_messages(question, [passage])))
        logits = self.model(**inputs).logits[0, -1, :].float()
        return torch.softmax(logits, dim=-1)[self.no_response_id].item()

    def score_and_answer(self, question: str, passage: dict, max_new_tokens: int):
        """P_nr and the single-passage answer from one generation call."""
        text, p_nr = self.generate(self.prompt(build_messages(question, [passage])),
                                   max_new_tokens, want_first_token_prob=True)
        return p_nr, text

    def answer(self, question: str, passages: list[dict], max_new_tokens: int) -> str:
        text, _ = self.generate(self.prompt(build_messages(question, passages)), max_new_tokens)
        return text

    def free_text(self, user_message: str, max_new_tokens: int) -> str:
        """Plain instruction without the RAG system prompt (used for Query2Doc)."""
        prompt = self.prompt([{"role": "user", "content": user_message}])
        inputs = self._encode(prompt)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                                      temperature=None, top_p=None, pad_token_id=self.tok.pad_token_id)
        return self.tok.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
