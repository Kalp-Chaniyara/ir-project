"""Figures for the report and slides (saved as PNG in figures/):

  fig1_distraction.png   How distracting the irrelevant passages are, one panel per pipeline
  fig2_ndcg_vs_udcg.png  nDCG vs UDCG per question, coloured by answer outcome
  fig3_outcomes.png      % correct / abstain / wrong for every setup
  fig4_correlation.png   Baseline B: our correlations next to the paper's

Run (Zeel):  python scripts/12_figures.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, SETUP_NAMES, SETUPS  # noqa: E402

# Colours: categorical slots for pipelines, status colours for answer outcomes.
SERIES = {"S1": "#2a78d6", "S2": "#eb6834", "S3": "#1baf7a", "S4": "#eda100"}
OUTCOME = {"correct": "#0ca30c", "abstain": "#fab219", "wrong": "#d03b3b"}
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
})


def save(fig, name):
    out = PATHS["figures"] / name
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", out.relative_to(ROOT))


def fig1(de):
    """Small multiples: each pipeline's histogram of DE, with its mean and hard-distractor share labelled."""
    fig, axes = plt.subplots(1, 4, figsize=(12, 3), sharey=True)
    bins = np.linspace(0, 1, 11)
    for ax, s in zip(axes, SETUPS):
        d = de[de.setup == s]["de"]
        w = np.ones(len(d)) / max(len(d), 1) * 100
        ax.hist(d, bins=bins, weights=w, color=SERIES[s], edgecolor="#fcfcfb", linewidth=2)
        ax.set_title(f"{s}: {SETUP_NAMES[s]}", color=INK, fontsize=9)
        ax.text(0.03, 0.95, f"mean DE {d.mean():.2f}\nDE > 0.8: {(d > 0.8).mean()*100:.0f}%",
                transform=ax.transAxes, va="top", fontsize=8, color=INK)
        ax.set_xlabel("distracting effect (DE)")
    axes[0].set_ylabel("% of irrelevant passages")
    fig.suptitle("How distracting are the irrelevant passages each pipeline retrieves?", color=INK,
                 x=0.01, y=1.08, ha="left")
    save(fig, "fig1_distraction.png")


def fig2(pq):
    d = pq[pq.setup.isin(SETUPS)].dropna(subset=["udcg", "outcome"])
    fig, ax = plt.subplots(figsize=(6, 4.5))
    rng = np.random.default_rng(0)
    for o in ["correct", "abstain", "wrong"]:
        x = d[d.outcome == o]
        ax.scatter(x["ndcg"] + rng.uniform(-0.01, 0.01, len(x)), x["udcg"], s=18, alpha=0.75,
                   color=OUTCOME[o], edgecolor="#fcfcfb", linewidth=0.8, label=f"{o} ({len(x)})")
    ax.set_xlabel("nDCG@5 (relevance only)")
    ax.set_ylabel("UDCG (relevance + distraction)")
    ax.set_title("Same nDCG, different UDCG: wrong answers tend to sit lower", loc="left", color=INK)
    ax.legend(frameon=False, title="answer outcome")
    save(fig, "fig2_ndcg_vs_udcg.png")


def fig3(t3):
    t3 = t3.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(t3) + 1))
    left = np.zeros(len(t3))
    for o in ["correct", "abstain", "wrong"]:
        vals = t3[f"{o} %"].to_numpy()
        ax.barh(t3["name"], vals, left=left, color=OUTCOME[o], edgecolor="#fcfcfb", linewidth=2, label=o)
        for y, (l, v) in enumerate(zip(left, vals)):
            if v >= 8:
                ax.text(l + v / 2, y, f"{v:.0f}", ha="center", va="center", fontsize=8,
                        color="#0b0b0b" if o == "abstain" else "#ffffff")
        left += vals
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of questions")
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, ncol=3, loc="lower right", bbox_to_anchor=(1, 1))
    ax.set_title("RAG answer outcome per setup", loc="left", color=INK)
    save(fig, "fig3_outcomes.png")


def fig4(t4):
    # Pooled is our main result; per question is the robustness check (see 10_correlation_analysis.py).
    cols = [("ours (pooled)", "#2a78d6"), ("ours (per question)", "#9ec5ef"), ("paper (Table 3)", "#eb6834")]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    x = np.arange(len(t4))
    w = 0.27
    for i, (col, color) in enumerate(cols):
        bars = ax.bar(x + (i - 1) * w, t4[col], w - 0.03, color=color, label=col)
        for b, v in zip(bars, t4[col]):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center", fontsize=7, color=INK)
    ax.set_xticks(x, t4.index)
    ax.set_ylabel("Spearman correlation\nwith answer outcome")
    names = [c for c, _ in cols]
    ax.set_ylim(min(0, t4[names].min().min() - 0.05), t4[names].max().max() + 0.08)
    ax.legend(frameon=False, ncol=3, loc="lower right", bbox_to_anchor=(1, 1.0))
    ax.set_title("Which metric predicts the LLM's answer? (Llama-3.2-3B, NQ)", loc="left", color=INK, pad=24)
    save(fig, "fig4_correlation.png")


def main():
    t = PATHS["tables"]
    if (t / "passage_de.csv").exists():
        fig1(pd.read_csv(t / "passage_de.csv"))
    if (t / "per_question.csv").exists():
        fig2(pd.read_csv(t / "per_question.csv", dtype={"qid": str}))
    if (t / "table3_answers.csv").exists():
        fig3(pd.read_csv(t / "table3_answers.csv"))
    if (t / "table4_correlation.csv").exists():
        fig4(pd.read_csv(t / "table4_correlation.csv", index_col=0))


if __name__ == "__main__":
    main()
