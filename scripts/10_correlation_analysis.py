"""Baseline B, analysis part: which metric best predicts whether the LLM answers correctly?

For each question we have 10 contexts and the LLM's answer to each (from Kalp's
09_correlation_run.py). Each answer is scored correct = 2, abstain = 1, wrong = 0 (the paper's
ideal ranking). Each metric also scores the 10 contexts. We compute the Spearman correlation
between the metric's scores and the answer scores in two ways. Higher = the metric ranks
contexts more like the LLM's real outcome.

  * pooled (main result): one correlation over all contexts of all questions together;
  * per question (robustness check): one correlation per question, then averaged.

The paper reports, for Llama-3.2-3B on NQ: nDCG 0.458, Precision 0.482, UDCG 0.536.

Choices the paper does not spell out (stated in our report):
  * pooled vs per question: the paper reports over "500 query-context examples" and its code
    does not include this experiment. Pooled reproduces the paper's numbers for nDCG, MRR,
    Precision and Hits (metrics that do not involve UDCG) much more closely, so it is our
    main result; the per-question version is reported alongside it;
  * per question only: questions where all 10 answers have the same outcome are skipped
    (Spearman undefined), and a metric that gives all 10 contexts the same score counts as 0.

Also checks that our P_nr values match the paper's (pnr_check.jsonl).

Run (Zeel):  python scripts/10_correlation_analysis.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, read_jsonl, write_json  # noqa: E402
from src.metrics import OUTCOME_SCORE, answer_outcome, hit_at_k, mrr, ndcg, precision_at_k, udcg  # noqa: E402

METRICS = ["nDCG", "MRR", "Precision", "Hits", "UDCG"]


def score_context(r: dict, gamma: float) -> dict:
    rels = [int(p["is_relevant"]) for p in r["passages"]]
    p_nrs = [p["p_nr_paper"] for p in r["passages"]]
    return {"nDCG": ndcg(rels, r["n_relevant_total"]), "MRR": mrr(rels), "Precision": precision_at_k(rels),
            "Hits": hit_at_k(rels), "UDCG": udcg(rels, p_nrs, gamma)}


def main():
    cfg = load_config()
    gamma = cfg["metrics"]["gamma"]
    rows = read_jsonl(PATHS["repro"] / "contexts.jsonl")
    df = pd.DataFrame([{"qid": r["qid"], "ctx_id": r["ctx_id"], "kind": r["kind"],
                        "outcome": answer_outcome(r["answer"], r["answers"],
                                                  any(p["is_relevant"] for p in r["passages"])),
                        **score_context(r, gamma)} for r in rows])
    df["outcome_score"] = df["outcome"].map(OUTCOME_SCORE)

    per_q, skipped = [], 0
    for qid, g in df.groupby("qid"):
        if g["outcome_score"].nunique() < 2:
            skipped += 1
            continue
        row = {"qid": qid}
        for m in METRICS:
            row[m] = 0.0 if g[m].nunique() < 2 else spearmanr(g[m], g["outcome_score"]).statistic
        per_q.append(row)
    per_q = pd.DataFrame(per_q, columns=["qid"] + METRICS)
    if per_q.empty:
        sys.exit("Every question got the same outcome in all 10 contexts, so no correlation can be computed. "
                 "Check results/repro/contexts.jsonl: are the answers sensible?")

    paper = cfg["paper_table3_llama3b_nq"]
    pooled = pd.Series({m: spearmanr(df[m], df["outcome_score"]).statistic for m in METRICS})
    t4 = pd.DataFrame({"ours (pooled)": pooled, "ours (per question)": per_q[METRICS].mean(),
                       "paper (Table 3)": pd.Series(paper)}).reindex(METRICS)
    t4["pooled - paper"] = t4["ours (pooled)"] - t4["paper (Table 3)"]
    t4["per question - paper"] = t4["ours (per question)"] - t4["paper (Table 3)"]
    tables = PATHS["tables"]
    tables.mkdir(parents=True, exist_ok=True)
    t4.round(3).to_csv(tables / "table4_correlation.csv")
    df.to_csv(tables / "repro_contexts_scored.csv", index=False)

    print("=== Table 4: Spearman correlation with answer outcome (Llama-3.2-3B, NQ) ===")
    print(t4.round(3).to_string())
    print(f"\nPooled: {len(df)} contexts from {df['qid'].nunique()} questions. "
          f"Per question: {len(per_q)} questions (skipped {skipped} where all 10 answers had the same outcome)")
    print("Outcome shares:", (df["outcome"].value_counts(normalize=True) * 100).round(1).to_dict())
    for col in ["ours (pooled)", "ours (per question)"]:
        print(f"{col:20s} best metric: {t4[col].idxmax():9s} UDCG beats nDCG: "
              f"{t4.loc['UDCG', col] > t4.loc['nDCG', col]}")

    # ---- P_nr check: do our scores match the paper's?
    chk = pd.DataFrame(read_jsonl(PATHS["repro"] / "pnr_check.jsonl"))
    hard = cfg["metrics"]["hard_distractor_threshold"]
    irr = chk[~chk.is_relevant]
    check = {
        "pairs": len(chk),
        "spearman": float(spearmanr(chk.p_nr_ours, chk.p_nr_paper).statistic),
        "pearson": float(pearsonr(chk.p_nr_ours, chk.p_nr_paper).statistic),
        "mean_abs_diff": float(np.mean(np.abs(chk.p_nr_ours - chk.p_nr_paper))),
        "hard_distractor_agreement": float(((1 - irr.p_nr_ours > hard) == (1 - irr.p_nr_paper > hard)).mean()),
    }
    write_json({"table4": t4.round(4).to_dict(), "questions_used": len(per_q), "skipped": skipped,
                "pnr_check": check}, tables / "repro_summary.json")
    print("\n=== Our P_nr vs the paper's P_nr (same passages, same model) ===")
    for k, v in check.items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"\nSaved {tables.relative_to(ROOT)}/table4_correlation.csv and repro_summary.json")


if __name__ == "__main__":
    main()
