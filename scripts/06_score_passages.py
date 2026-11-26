"""Gives every passage in the S1-S4 contexts to the LLM on its own, with the paper's prompt:
"answer from this document, or reply NO-RESPONSE".

For each (question, passage) we save:
  p_nr   = probability that the LLM's first token is NO-RESPONSE (the paper's measure)
  answer = what the LLM actually answered from this passage alone (used by the filter)

Distracting effect of an irrelevant passage = 1 - p_nr.
The same passage often appears in several pipelines, so each pair is scored once.

Run (Kalp, Mac):
  python scripts/06_score_passages.py --limit 20     # quick check on 20 questions first
  python scripts/06_score_passages.py                # full run, continues where it stopped
"""
import argparse
import json
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, SETUPS, load_config, read_jsonl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only the first N questions (sanity check)")
    args = ap.parse_args()
    cfg = load_config()

    # Collect unique (question, passage) pairs from the four contexts.
    pairs, seen = [], set()
    contexts = {s: read_jsonl(PATHS["contexts"] / f"{s}.jsonl") for s in SETUPS}
    qids = [r["qid"] for r in contexts["S1"]][: args.limit]
    keep_q = set(qids)
    for s in SETUPS:
        for row in contexts[s]:
            if row["qid"] not in keep_q:
                continue
            for p in row["passages"]:
                key = (row["qid"], p["pid"])
                if key not in seen:
                    seen.add(key)
                    pairs.append((row["question"], row["qid"], p))

    out_path = PATHS["llm"] / "passage_scores.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["qid"], r["pid"]) for r in read_jsonl(out_path)} if out_path.exists() else set()
    todo = [x for x in pairs if (x[1], x[2]["pid"]) not in done]
    print(f"{len(pairs)} unique question-passage pairs, {len(done & seen)} already scored, {len(todo)} to go")

    if todo:
        from src.llm import LocalLLM
        llm = LocalLLM(cfg["models"]["llm"], cfg["llm"]["dtype"])
        with open(out_path, "a", encoding="utf-8") as f:
            for question, qid, p in tqdm(todo, desc="scoring passages"):
                p_nr, ans = llm.score_and_answer(question, p, cfg["llm"]["passage_max_new_tokens"])
                f.write(json.dumps({"qid": qid, "pid": p["pid"], "has_answer": p["has_answer"],
                                    "p_nr": p_nr, "answer": ans}, ensure_ascii=False) + "\n")
                f.flush()

    # Quick summary so we can see if the LLM behaves sensibly.
    rows = [r for r in read_jsonl(out_path) if r["qid"] in keep_q]
    rel = [r for r in rows if r["has_answer"]]
    irr = [r for r in rows if not r["has_answer"]]

    def mean(xs):
        return sum(xs) / len(xs) if xs else float("nan")

    print(f"\nScored pairs: {len(rows)}  (relevant {len(rel)}, irrelevant {len(irr)})")
    print(f"Mean P(NO-RESPONSE): relevant {mean([r['p_nr'] for r in rel]):.3f} | "
          f"irrelevant {mean([r['p_nr'] for r in irr]):.3f}   (expect relevant much lower)")
    print(f"Share answered NO-RESPONSE: relevant "
          f"{mean([('NO-RESPONSE' in r['answer'].upper()) for r in rel]):.2f} | irrelevant "
          f"{mean([('NO-RESPONSE' in r['answer'].upper()) for r in irr]):.2f}")
    hard = [r for r in irr if 1 - r["p_nr"] > cfg["metrics"]["hard_distractor_threshold"]]
    print(f"Hard distractors (DE > {cfg['metrics']['hard_distractor_threshold']}): {len(hard)} of {len(irr)} irrelevant")
    print(f"Saved to {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
