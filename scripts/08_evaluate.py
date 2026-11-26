"""Evaluation: turns contexts, passage scores and RAG answers into the result tables.

Works in two stages, so it can be run before the LLM results exist:
  * contexts only (Day 4)          -> retrieval metrics: Hit@5, Precision@5, MRR, nDCG@5
  * + passage_scores + rag_answers -> distraction (DE), UDCG, answer accuracy, significance tests

Outputs (results/tables/):
  table2_retrieval.csv    retrieval quality and distraction per setup      (answers RQ1, RQ2)
  table3_answers.csv      % correct / abstain / wrong per setup + p-values (answers RQ4)
  stats.json              Wilcoxon tests and the "nDCG up but UDCG down" count
  per_question.csv        one row per (setup, question), used by the figures
  passage_de.csv          one row per irrelevant passage with its DE, used by the figures

Run (Zeel):  python scripts/08_evaluate.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, SETUP_NAMES, SETUPS, load_config, read_json, read_jsonl, write_json  # noqa: E402
from src.metrics import (answer_outcome, distracting_effect, hit_at_k, mcnemar_exact, mrr, ndcg,  # noqa: E402
                         precision_at_k, udcg, wilcoxon_p)

ALL_SETUPS = SETUPS + [s + "F" for s in SETUPS] + ["ORACLE"]


def setup_label(s: str) -> str:
    if s == "ORACLE":
        return "Oracle (S4, gold-filtered)"
    if s.endswith("F"):
        return SETUP_NAMES[s[:-1]] + " + filter"
    return SETUP_NAMES[s]


def main():
    cfg = load_config()
    gamma = cfg["metrics"]["gamma"]
    hard_t = cfg["metrics"]["hard_distractor_threshold"]
    tables = PATHS["tables"]
    tables.mkdir(parents=True, exist_ok=True)

    contexts = {s: read_jsonl(PATHS["contexts"] / f"{s}.jsonl") for s in SETUPS}
    pool = read_json(PATHS["contexts"] / "pool.json")
    questions = {r["qid"]: r for r in contexts["S1"]}
    passages = {(r["qid"], p["pid"]): p for s in SETUPS for r in contexts[s] for p in r["passages"]}

    scores_path = PATHS["llm"] / "passage_scores.jsonl"
    answers_path = PATHS["llm"] / "rag_answers.jsonl"
    have_llm = scores_path.exists() and answers_path.exists()
    scores = {(r["qid"], r["pid"]): r["p_nr"] for r in read_jsonl(scores_path)} if have_llm else {}

    # Which passages each setup gave the LLM.
    ctx_pids = {(s, r["qid"]): [p["pid"] for p in r["passages"]] for s in SETUPS for r in contexts[s]}
    answers = {}
    if have_llm:
        for r in read_jsonl(answers_path):
            ctx_pids[(r["setup"], r["qid"])] = r["pids"]
            answers[(r["setup"], r["qid"])] = r["answer"]

    rows, de_rows = [], []
    for (s, qid), pids in ctx_pids.items():
        if qid not in questions:
            continue
        rels = [int(passages[(qid, pid)]["has_answer"]) for pid in pids]
        row = {"setup": s, "qid": qid, "n_passages": len(pids), "hit": hit_at_k(rels),
               "precision": precision_at_k(rels) if rels else 0.0, "n_irrelevant": rels.count(0)}
        if s in SETUPS:  # rank-based metrics only make sense for the full ranked top-5
            row["mrr"] = mrr(rels)
            row["ndcg"] = ndcg(rels, pool[qid])
        if have_llm and all((qid, pid) in scores for pid in pids):
            p_nrs = [scores[(qid, pid)] for pid in pids]
            des = [distracting_effect(p) for p, r in zip(p_nrs, rels) if not r]
            row["udcg"] = udcg(rels, p_nrs, gamma)
            row["de_sum"] = sum(des)                         # total distraction in the context
            row["de_mean_irrelevant"] = np.mean(des) if des else np.nan
            row["n_hard"] = sum(d > hard_t for d in des)
            if s in SETUPS:
                de_rows += [{"setup": s, "qid": qid, "pid": pid, "de": distracting_effect(p)}
                            for pid, p, r in zip(pids, p_nrs, rels) if not r]
        if (s, qid) in answers:
            row["answer"] = answers[(s, qid)]
            row["outcome"] = answer_outcome(answers[(s, qid)], questions[qid]["answers"], any(rels))
        rows.append(row)

    df = pd.DataFrame(rows)
    df["setup_name"] = df["setup"].map(setup_label)
    order = [s for s in ALL_SETUPS if s in set(df["setup"])]
    df.to_csv(tables / "per_question.csv", index=False)
    if de_rows:
        pd.DataFrame(de_rows).to_csv(tables / "passage_de.csv", index=False)

    # ---------------- Table 2: retrieval quality and distraction
    agg = {"hit": "mean", "precision": "mean", "n_passages": "mean", "n_irrelevant": "mean"}
    for c in ["mrr", "ndcg", "de_mean_irrelevant", "n_hard", "de_sum", "udcg"]:
        if c in df:
            agg[c] = "mean"
    t2 = df.groupby("setup").agg(agg).reindex(order)
    for c in ["hit", "precision"]:
        t2[c] = 100 * t2[c]
    t2.insert(0, "name", [setup_label(s) for s in t2.index])
    t2 = t2.rename(columns={"hit": "Hit@5 %", "precision": "Precision %", "mrr": "MRR", "ndcg": "nDCG@5",
                            "n_passages": "passages/q", "n_irrelevant": "irrelevant/q",
                            "de_mean_irrelevant": "mean DE (irrelevant)", "n_hard": "hard distractors/q",
                            "de_sum": "total DE/q", "udcg": "UDCG"})
    t2.round(3).to_csv(tables / "table2_retrieval.csv")
    print("\n=== Table 2: retrieval and distraction (mean per question) ===")
    print(t2.round(3).to_string())

    if not have_llm:
        print("\nLLM outputs not found yet: only retrieval metrics computed. Re-run after Kalp's Day 4 push.")
        return

    # ---------------- Table 3: answer outcomes
    ans = df.dropna(subset=["outcome"])
    correct = {s: ans[ans.setup == s].set_index("qid")["outcome"].eq("correct") for s in order}
    t3 = []
    for s in order:
        o = ans[ans.setup == s]["outcome"]
        row = {"setup": s, "name": setup_label(s), "n": len(o),
               "correct %": 100 * (o == "correct").mean(), "abstain %": 100 * (o == "abstain").mean(),
               "wrong %": 100 * (o == "wrong").mean()}
        base = "S1" if s in SETUPS or s == "ORACLE" else s[:-1]  # filtered setups vs their unfiltered version
        if s != "S1":
            a, b = correct[base].align(correct[s], join="inner")
            row["compared with"] = base
            row["McNemar p"] = mcnemar_exact(list(a), list(b))
        t3.append(row)
    t3 = pd.DataFrame(t3).set_index("setup")
    t3.round(4).to_csv(tables / "table3_answers.csv")
    print("\n=== Table 3: RAG answer outcomes ===")
    print(t3.round(3).to_string())

    # ---------------- significance of retrieval/distraction changes vs S1
    stats = {"wilcoxon_vs_S1": {}, "ndcg_up_udcg_down": {}}
    base = df[df.setup == "S1"].set_index("qid")
    for s in ["S2", "S3", "S4"]:
        other = df[df.setup == s].set_index("qid")
        a, b = base.align(other, join="inner", axis=0)
        stats["wilcoxon_vs_S1"][s] = {m: {"mean_S1": float(a[m].mean()), f"mean_{s}": float(b[m].mean()),
                                          "p": wilcoxon_p(list(a[m]), list(b[m]))}
                                      for m in ["ndcg", "udcg", "de_sum", "n_hard"]}
        both = (b["ndcg"] >= a["ndcg"]) & (b["udcg"] < a["udcg"])
        stats["ndcg_up_udcg_down"][s] = {
            "questions": int(both.sum()),
            "of_which_S1_correct_but_this_not": int((both & correct["S1"].reindex(a.index).fillna(False)
                                                     & ~correct[s].reindex(a.index).fillna(False)).sum())}
    filt = pd.read_json(PATHS["llm"] / "filter_decisions.jsonl", lines=True, dtype={"qid": str})
    filt["n_dropped"] = filt["dropped"].str.len()
    stats["filter"] = {s: {"mean_dropped": float(g["n_dropped"].mean()),
                           "share_questions_changed": float((g["n_dropped"] > 0).mean())}
                       for s, g in filt.groupby("setup")}
    write_json(stats, tables / "stats.json")
    print("\n=== Significance vs S1 (Wilcoxon) and 'nDCG same or higher but UDCG lower' counts ===")
    for s, v in stats["wilcoxon_vs_S1"].items():
        print(s, {m: f"{x[f'mean_{s}']:.3f} vs {x['mean_S1']:.3f} (p={x['p']:.3g})" for m, x in v.items()},
              "| nDCG>=, UDCG<:", stats["ndcg_up_udcg_down"][s])
    print(f"\nSaved tables to {tables.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
