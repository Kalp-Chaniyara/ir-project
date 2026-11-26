"""Final RAG answers: the LLM reads a whole context (up to 5 passages) and answers.

Setups answered:
  S1..S4      the four pipelines' top-5 contexts
  S1F..S4F    the same contexts after our distractor filter (src/filter.py, written by Zeel)
  ORACLE      S4 with every irrelevant passage removed using the gold answers
              (an upper bound, not a real system: it cheats with the answer)

Identical contexts are answered once (for example, when the filter keeps all 5 passages).
Also saves what the filter kept and dropped, for the analysis.

Run (Kalp, Mac):  python scripts/07_rag_answers.py      (needs 06_score_passages.py first)
"""
import argparse
import json
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, SETUPS, load_config, read_jsonl, write_jsonl  # noqa: E402
from src.filter import majority_filter  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only the first N questions")
    args = ap.parse_args()
    cfg = load_config()

    contexts = {s: read_jsonl(PATHS["contexts"] / f"{s}.jsonl")[: args.limit] for s in SETUPS}
    scores = {(r["qid"], r["pid"]): r for r in read_jsonl(PATHS["llm"] / "passage_scores.jsonl")}

    # Build every context to answer.
    jobs, decisions = [], []
    for s in SETUPS:
        for row in contexts[s]:
            ps = row["passages"]
            jobs.append((s, row, ps))
            single = [scores[(row["qid"], p["pid"])]["answer"] for p in ps]
            dec = majority_filter(single)
            kept = [ps[i] for i in dec["keep"]]
            jobs.append((s + "F", row, kept))
            decisions.append({"qid": row["qid"], "setup": s + "F", "kept": [p["pid"] for p in kept],
                              "dropped": [p["pid"] for p in ps if p not in kept],
                              "majority": dec["majority"], "reason": dec["reason"]})
            if s == "S4":
                jobs.append(("ORACLE", row, [p for p in ps if p["has_answer"]]))
    write_jsonl(decisions, PATHS["llm"] / "filter_decisions.jsonl")

    out_path = PATHS["llm"] / "rag_answers.jsonl"
    done = {(r["qid"], r["setup"]) for r in read_jsonl(out_path)} if out_path.exists() else set()
    cache = {(r["qid"], tuple(r["pids"])): r["answer"] for r in read_jsonl(out_path)} if out_path.exists() else {}
    todo = [j for j in jobs if (j[1]["qid"], j[0]) not in done]
    print(f"{len(jobs)} contexts in total, {len(todo)} still to answer")

    llm = None
    with open(out_path, "a", encoding="utf-8") as f:
        for setup, row, ps in tqdm(todo, desc="RAG answers"):
            key = (row["qid"], tuple(p["pid"] for p in ps))
            if key not in cache:
                if llm is None:
                    from src.llm import LocalLLM
                    llm = LocalLLM(cfg["models"]["llm"], cfg["llm"]["dtype"])
                cache[key] = llm.answer(row["question"], ps, cfg["llm"]["rag_max_new_tokens"])
            f.write(json.dumps({"qid": row["qid"], "setup": setup, "pids": list(key[1]),
                                "answer": cache[key]}, ensure_ascii=False) + "\n")
            f.flush()

    # Quick look at accuracy so we know the run worked (full evaluation is Zeel's 08_evaluate.py).
    from src.metrics import answer_outcome
    gold = {r["qid"]: r for r in contexts["S1"]}
    rel = {(r["qid"], p["pid"]): p["has_answer"] for s in SETUPS for r in contexts[s] for p in r["passages"]}
    by_setup = {}
    for r in read_jsonl(out_path):
        if r["qid"] not in gold:
            continue
        has_rel = any(rel.get((r["qid"], pid), False) for pid in r["pids"])
        by_setup.setdefault(r["setup"], []).append(answer_outcome(r["answer"], gold[r["qid"]]["answers"], has_rel))
    print(f"\n{'Setup':8s} {'correct':>8s} {'abstain':>8s} {'wrong':>8s}  (n)")
    for s in sorted(by_setup):
        o = by_setup[s]
        print(f"{s:8s} {100*o.count('correct')/len(o):8.1f} {100*o.count('abstain')/len(o):8.1f} "
              f"{100*o.count('wrong')/len(o):8.1f}  ({len(o)})")
    print(f"Saved to {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
