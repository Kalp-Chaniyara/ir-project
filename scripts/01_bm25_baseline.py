"""Baseline A: reproduce BM25 retrieval on Natural Questions (open) with Pyserini.

Runs the three commands from Pyserini's own DPR replication page, on all 3,610 test
questions, then compares our Top-20 / Top-100 accuracy with the published numbers.

Top-k accuracy = share of questions where at least one of the top k passages contains a gold answer.

Run (Kalp, Mac):  python scripts/01_bm25_baseline.py
Time: a few minutes once the index is downloaded.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, write_json  # noqa: E402

REFERENCE = {
    "DPR paper (Karpukhin et al., 2020)": {"top20": 59.1, "top100": 73.7},
    "Pyserini documented replication": {"top20": 62.99, "top100": 78.23},
}


def run(cmd: list[str]) -> str:
    print("\n$ " + " ".join(cmd), flush=True)
    out = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(out.stdout[-2000:])
    return out.stdout


def main():
    cfg = load_config()
    work = ROOT / "data" / "baseline_runs"          # large files, not committed
    work.mkdir(parents=True, exist_ok=True)
    trec = work / "run.bm25.dpr-nq-test.trec"
    dpr_json = work / "run.bm25.dpr-nq-test.json"
    py = sys.executable

    run([py, "-m", "pyserini.search.lucene",
         "--index", cfg["data"]["index"], "--topics", cfg["data"]["topics"],
         "--output", str(trec), "--bm25", "--hits", "100",
         "--threads", str(cfg["retrieval"]["threads"]), "--batch-size", "64"])
    run([py, "-m", "pyserini.eval.convert_trec_run_to_dpr_retrieval_run",
         "--index", cfg["data"]["index"], "--topics", cfg["data"]["topics"],
         "--input", str(trec), "--output", str(dpr_json)])
    out = run([py, "-m", "pyserini.eval.evaluate_dpr_retrieval",
               "--retrieval", str(dpr_json), "--topk", "20", "100"])

    ours = {}
    for k in (20, 100):
        m = re.search(rf"Top{k}\s+accuracy:\s*([0-9.]+)", out)
        ours[f"top{k}"] = round(100 * float(m.group(1)), 2) if m else None

    n_questions = sum(1 for _ in open(trec)) // 100
    result = {"ours": ours, "n_questions": n_questions, "reference": REFERENCE,
              "difference_vs_pyserini": {k: round(ours[k] - REFERENCE["Pyserini documented replication"][k], 2)
                                         for k in ours if ours[k] is not None}}
    write_json(result, PATHS["baseline_a"])

    print("\n=== Baseline A: BM25 on NQ-open test ===")
    print(f"{'Source':40s} {'Top-20':>8s} {'Top-100':>8s}")
    for name, v in REFERENCE.items():
        print(f"{name:40s} {v['top20']:8.2f} {v['top100']:8.2f}")
    print(f"{'Ours':40s} {ours['top20']:8.2f} {ours['top100']:8.2f}")
    print(f"\nQuestions evaluated: {n_questions}. Saved to {PATHS['baseline_a'].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
