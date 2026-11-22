"""Builds the four top-5 contexts the LLM will read, one per pipeline:

  S1 = BM25 top 5
  S2 = Query2Doc + BM25 top 5
  S3 = BM25 top 50, re-ordered by a cross-encoder, top 5
  S4 = Query2Doc + BM25 top 50, re-ordered by a cross-encoder, top 5

The cross-encoder (ms-marco-MiniLM-L-6-v2) reads the question and a passage together and
gives one relevance score. It is more accurate than BM25 but too slow to run on all 21M
passages, so it only re-orders BM25's top 50.

Also writes pool.json: for each question, how many relevant passages exist in S1 and S2's
top 50 combined. nDCG uses this as its "ideal" so every pipeline is judged against the same target.

Run (Zeel):  python scripts/05_rerank.py
Test on the small sample file:  python scripts/05_rerank.py --runs-dir tests/fixtures --out-dir tests/fixtures/out
"""
import argparse
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, read_jsonl, write_json, write_jsonl  # noqa: E402


def device() -> str:
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def to_context(row: dict, passages: list[dict]) -> dict:
    keep = ("pid", "title", "text", "has_answer", "rank", "score", "rerank_score")
    return {"qid": row["qid"], "question": row["question"], "answers": row["answers"],
            "passages": [{k: p[k] for k in keep if k in p} for p in passages]}


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default=str(PATHS["runs"]))
    ap.add_argument("--out-dir", default=str(PATHS["contexts"]))
    ap.add_argument("--k", type=int, default=cfg["retrieval"]["k"])
    args = ap.parse_args()
    runs_dir, out_dir, k = Path(args.runs_dir), Path(args.out_dir), args.k
    depth = cfg["retrieval"]["depth"]

    s1 = read_jsonl(runs_dir / f"S1_top{depth}.jsonl")
    s2 = read_jsonl(runs_dir / f"S2_top{depth}.jsonl")

    from sentence_transformers import CrossEncoder
    dev = device()
    print(f"Loading reranker {cfg['models']['reranker']} on {dev}")
    model = CrossEncoder(cfg["models"]["reranker"], device=dev)

    def rerank(rows, name):
        out = []
        for row in tqdm(rows, desc=f"rerank {name}"):
            pairs = [(row["question"], f"{p['title']}. {p['text']}") for p in row["hits"]]
            scores = model.predict(pairs, batch_size=64, show_progress_bar=False)
            ranked = sorted(zip(row["hits"], scores), key=lambda x: -float(x[1]))
            out.append(to_context(row, [dict(p, rerank_score=round(float(s), 4)) for p, s in ranked[:k]]))
        return out

    contexts = {
        "S1": [to_context(r, r["hits"][:k]) for r in s1],
        "S2": [to_context(r, r["hits"][:k]) for r in s2],
        "S3": rerank(s1, "S1 -> S3"),
        "S4": rerank(s2, "S2 -> S4"),
    }
    for name, rows in contexts.items():
        write_jsonl(rows, out_dir / f"{name}.jsonl")

    # Relevant passages known per question (union of both BM25 top-50 lists).
    pool = {}
    for a, b in zip(s1, s2):
        assert a["qid"] == b["qid"], "S1 and S2 files are not in the same question order"
        relevant = {p["pid"] for p in a["hits"] + b["hits"] if p["has_answer"]}
        pool[a["qid"]] = len(relevant)
    write_json(pool, out_dir / "pool.json")

    print(f"\nSaved contexts to {out_dir}")
    print(f"{'Setup':6s} {'Hit@'+str(k):>7s}  {'avg relevant in top '+str(k):>22s}")
    for name, rows in contexts.items():
        hit = 100 * sum(any(p["has_answer"] for p in r["passages"]) for r in rows) / len(rows)
        avg = sum(sum(p["has_answer"] for p in r["passages"]) for r in rows) / len(rows)
        print(f"{name:6s} {hit:7.1f}  {avg:22.2f}")


if __name__ == "__main__":
    main()
