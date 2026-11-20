"""Shared helpers used by every script: paths, config, JSONL files, prompts.

Nothing in here needs Pyserini or a GPU, so both laptops can import it.
"""
from __future__ import annotations

import ast
import json
import random
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

# Where each step writes its output. Every path is relative to the repo root.
RESULTS = ROOT / "results"
PATHS = {
    "baseline_a": RESULTS / "baseline_a.json",
    "sample": RESULTS / "sample_questions.jsonl",
    "q2d": RESULTS / "query2doc.jsonl",
    "runs": RESULTS / "runs",            # BM25 top-50 lists (Kalp)
    "contexts": RESULTS / "contexts",    # top-5 contexts for S1-S4 (Zeel)
    "llm": RESULTS / "llm",              # LLM outputs (Kalp)
    "tables": RESULTS / "tables",        # evaluation tables (Zeel)
    "repro": RESULTS / "repro",          # paper reproduction (Baseline B)
    "external": ROOT / "data" / "external",  # downloaded files, never committed
    "figures": ROOT / "figures",
}

SETUPS = ["S1", "S2", "S3", "S4"]
SETUP_NAMES = {
    "S1": "BM25",
    "S2": "Query2Doc + BM25",
    "S3": "BM25 + reranker",
    "S4": "Query2Doc + BM25 + reranker",
}

# The exact system prompt from the paper's code (GiovanniTRA/UDCG, src/compute_abstention_probability.py).
SYSTEM_PROMPT = (
    "You are given a question and you must respond based on the provided documents. "
    "Respond directly without providing any premise or explanation. "
    "If none of the documents contain the answer, please respond with NO-RESPONSE. "
    "Do not try to respond based on your own knowledge."
)
NO_RESPONSE = "NO-RESPONSE"


def load_config() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def set_seed(seed: int) -> None:
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass


def read_jsonl(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(rows, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(obj, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_answers(raw) -> list[str]:
    """Pyserini stores NQ answers as the text of a Python list, sometimes wrapped in quotes.
    Same handling as pyserini/eval/convert_trec_run_to_dpr_retrieval_run.py, but with
    ast.literal_eval instead of eval."""
    if isinstance(raw, list):
        return [str(a) for a in raw]
    raw = str(raw)
    if raw.startswith('"'):
        raw = raw[1:-1].replace('""', '"')
    return [str(a) for a in ast.literal_eval(raw)]


def passage_for_llm(p: dict) -> str:
    """How a passage is shown to the LLM: title first, like the paper's '(Title: ...)' format.
    Passages from the paper's own dataset already start with '(Title: ...)', so they have no title field."""
    if p.get("title"):
        return f"(Title: {p['title']}) {p['text']}"
    return p["text"]


def build_messages(question: str, passages: list[dict]) -> list[dict]:
    """Chat messages for answering from 0..k passages.

    One passage gives exactly the paper's single-passage prompt ("Document: ...").
    Several passages are numbered "Document 1:", "Document 2:", ...
    """
    if len(passages) == 1:
        docs = f"Document: {passage_for_llm(passages[0])}\n"
    elif passages:
        docs = "".join(f"Document {i}: {passage_for_llm(p)}\n" for i, p in enumerate(passages, 1))
    else:
        docs = "Document: (no documents retrieved)\n"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{docs}Question: {question}\nAnswer:"},
    ]
