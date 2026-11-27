"""Hand-picked examples for the report and slides (written to results/examples.md):

  A. Query expansion brought in distractors: S2's nDCG is the same or higher than S1's, S2 has more
     hard distractors, and the answer went from correct (S1) to not correct (S2).
  B. The filter helped: S4 not correct -> S4 + filter correct.
  C. The filter hurt: S4 correct -> S4 + filter not correct.

Uses Zeel's results/tables/per_question.csv, so run after his Day 5 push.

Run (Kalp):  python scripts/11_examples.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, SETUP_NAMES, SETUPS, read_jsonl  # noqa: E402


def main():
    pq = pd.read_csv(PATHS["tables"] / "per_question.csv", dtype={"qid": str})
    wide = {s: g.set_index("qid") for s, g in pq.groupby("setup")}
    contexts = {s: {r["qid"]: r for r in read_jsonl(PATHS["contexts"] / f"{s}.jsonl")} for s in SETUPS}
    scores = {(r["qid"], r["pid"]): r for r in read_jsonl(PATHS["llm"] / "passage_scores.jsonl")}
    decisions = {(r["setup"], r["qid"]): r for r in read_jsonl(PATHS["llm"] / "filter_decisions.jsonl")}

    s1, s2, s4, s4f = wide["S1"], wide["S2"], wide["S4"], wide["S4F"]
    common = s1.index.intersection(s2.index)
    a = [q for q in common if s2.at[q, "ndcg"] >= s1.at[q, "ndcg"] and s2.at[q, "n_hard"] > s1.at[q, "n_hard"]
         and s1.at[q, "outcome"] == "correct" and s2.at[q, "outcome"] != "correct"]
    a = sorted(a, key=lambda q: s1.at[q, "n_hard"] - s2.at[q, "n_hard"])[:3]
    b = [q for q in s4.index if s4.at[q, "outcome"] != "correct" and s4f.at[q, "outcome"] == "correct"][:2]
    c = [q for q in s4.index if s4.at[q, "outcome"] == "correct" and s4f.at[q, "outcome"] != "correct"][:2]

    def show(setup, qid):
        ctx = contexts[setup[:2]][qid]
        row = wide[setup].loc[qid]
        lines = [f"**{setup} ({SETUP_NAMES[setup[:2]]}{' + filter' if setup.endswith('F') else ''})**: "
                 f"answer *{row['answer']}* ({row['outcome']}), nDCG {row.get('ndcg', float('nan')):.2f}, "
                 f"UDCG {row['udcg']:.2f}, hard distractors {int(row['n_hard'])}", ""]
        kept = decisions.get((setup, qid), {}).get("kept")
        for i, p in enumerate(ctx["passages"], 1):
            sc = scores[(qid, p["pid"])]
            tag = "RELEVANT" if p["has_answer"] else f"irrelevant, DE {1 - sc['p_nr']:.2f}"
            drop = "" if kept is None or p["pid"] in kept else " **[dropped by filter]**"
            lines.append(f"{i}. ({tag}) *{p['title']}*: {p['text'][:220]}... -> LLM alone says: "
                         f"\"{sc['answer']}\"{drop}")
        return "\n".join(lines) + "\n"

    out = ["# Qualitative examples\n",
           f"Counts: expansion-distractor cases {len(a)} shown, filter helped {len(b)}, filter hurt {len(c)}.\n"]
    for title, qs, setups in [("A. Query expansion brought in distractors", a, ["S1", "S2"]),
                              ("B. The filter helped", b, ["S4", "S4F"]),
                              ("C. The filter hurt", c, ["S4", "S4F"])]:
        out.append(f"\n## {title}\n")
        if not qs:
            out.append("No such question in our sample.\n")
        for q in qs:
            ctx = contexts["S1"][q]
            out.append(f"\n### Q: {ctx['question']}\nGold answers: {ctx['answers']}\n")
            out += [show(s, q) for s in setups]

    path = ROOT / "results" / "examples.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"A: {len(a)}  B: {len(b)}  C: {len(c)}  -> saved {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
