"""Baseline B, LLM part: reproduce the paper's metric-correlation experiment on the paper's own data.

The paper released its NQ data (github.com/GiovanniTRA/UDCG, data/datasets/nq_dataset.json):
1,000 questions, each with 25 retrieved passages, relevance labels and the P_nr values they
measured with Llama-3.2-3B. We use it in two ways:

1. P_nr check: re-score all 25 passages of 40 questions with OUR code and model, and save our
   P_nr next to the paper's. If they match, our distraction scores are computed the same way.
2. Correlation experiment (as in the paper, Section 7.2): for 200 questions build 10 contexts of
   5 passages from the 25 (5 contexts with at least one relevant passage, 5 with none), let the
   LLM answer each, and save the answers. Zeel's scripts/10_correlation_analysis.py then checks
   which metric (nDCG, Precision, UDCG...) best predicts whether each answer is correct.

Run (Kalp, Mac, overnight):  python scripts/09_correlation_run.py
Safe to stop and re-run: finished work is skipped.
"""
import json
import random
import sys
import urllib.request
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, read_json, read_jsonl  # noqa: E402


def load_paper_data(cfg) -> list[dict]:
    path = PATHS["external"] / "udcg_nq_dataset.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading the paper's NQ data (about 45 MB) to {path.relative_to(ROOT)} ...")
        urllib.request.urlretrieve(cfg["repro"]["udcg_data_url"], path)
    return read_json(path)


def build_contexts(item: dict, n_ctx: int, size: int, rng: random.Random) -> list[dict]:
    """Half the contexts contain at least one relevant passage, half contain none (as in the paper).
    Passages inside a context keep the retriever's order."""
    ps = item["passages"]
    rel = [i for i, p in enumerate(ps) if p["is_relevant"]]
    irr = [i for i, p in enumerate(ps) if not p["is_relevant"]]
    out = []
    for c in range(n_ctx):
        if c < n_ctx // 2:
            first = rng.choice(rel)
            rest = rng.sample([i for i in range(len(ps)) if i != first], size - 1)
            idx = [first] + rest
            kind = "with_relevant"
        else:
            idx = rng.sample(irr, size)
            kind = "irrelevant_only"
        out.append({"ctx_id": c, "kind": kind, "idx": sorted(idx, key=lambda i: ps[i]["rank"])})
    return out


def main():
    cfg = load_config()
    rc = cfg["repro"]
    key = rc["paper_model_key"]
    data = load_paper_data(cfg)

    # Questions with at least 1 relevant and at least 5 irrelevant passages (needed to build both kinds).
    usable = [x for x in data
              if 1 <= sum(p["is_relevant"] for p in x["passages"]) <= len(x["passages"]) - rc["context_size"]]
    rng = random.Random(cfg["seed"])
    chosen = rng.sample(usable, rc["n_questions"])
    print(f"{len(data)} questions in the paper's data, {len(usable)} usable, using {len(chosen)}")

    out_dir = PATHS["repro"]
    out_dir.mkdir(parents=True, exist_ok=True)
    from src.llm import LocalLLM
    llm = None

    def get_llm():
        nonlocal llm
        if llm is None:
            llm = LocalLLM(cfg["models"]["llm"], cfg["llm"]["dtype"])
        return llm

    # ---- 1. P_nr check
    check_path = out_dir / "pnr_check.jsonl"
    done = {(r["qid"], r["doc_id"]) for r in read_jsonl(check_path)} if check_path.exists() else set()
    with open(check_path, "a", encoding="utf-8") as f:
        todo = [(x, p) for x in chosen[: rc["pnr_check_questions"]] for p in x["passages"]
                if (x["example_id"], p["doc_id"]) not in done]
        for x, p in tqdm(todo, desc="P_nr check"):
            ours = get_llm().p_no_response(x["question"], {"text": p["text"]})
            f.write(json.dumps({"qid": x["example_id"], "doc_id": p["doc_id"], "is_relevant": p["is_relevant"],
                                "p_nr_ours": ours, "p_nr_paper": p["models_info"][key]["no_res_prob"]}) + "\n")
            f.flush()

    # ---- 2. Contexts and answers
    ctx_path = out_dir / "contexts.jsonl"
    done = {(r["qid"], r["ctx_id"]) for r in read_jsonl(ctx_path)} if ctx_path.exists() else set()
    jobs = []
    for x in chosen:
        n_rel_total = sum(p["is_relevant"] for p in x["passages"])
        for c in build_contexts(x, rc["contexts_per_question"], rc["context_size"], rng):
            if (x["example_id"], c["ctx_id"]) not in done:
                jobs.append((x, c, n_rel_total))
    with open(ctx_path, "a", encoding="utf-8") as f:
        for x, c, n_rel_total in tqdm(jobs, desc="answering contexts"):
            ps = [x["passages"][i] for i in c["idx"]]
            ans = get_llm().answer(x["question"], [{"text": p["text"]} for p in ps], cfg["llm"]["rag_max_new_tokens"])
            f.write(json.dumps({
                "qid": x["example_id"], "question": x["question"], "answers": x["answers"],
                "ctx_id": c["ctx_id"], "kind": c["kind"], "n_relevant_total": n_rel_total,
                "passages": [{"doc_id": p["doc_id"], "rank": p["rank"], "is_relevant": p["is_relevant"],
                              "p_nr_paper": p["models_info"][key]["no_res_prob"]} for p in ps],
                "answer": ans}, ensure_ascii=False) + "\n")
            f.flush()

    print(f"\nSaved {check_path.relative_to(ROOT)} and {ctx_path.relative_to(ROOT)}")
    print(f"Contexts answered: {len(read_jsonl(ctx_path))}  |  P_nr pairs checked: {len(read_jsonl(check_path))}")


if __name__ == "__main__":
    main()
