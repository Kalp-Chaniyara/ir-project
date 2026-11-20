# When Better Retrieval Misleads the LLM

IT550 Information Retrieval course project, DA-IICT (Dhirubhai Ambani University). Prof. Sandip Modha.
Team: Kalp Chaniyara, Zeel Dadhaniya.

## What this project does

In RAG, the LLM reads every passage the retriever returns. Some irrelevant passages are harmless
(a recipe in the results for a cricket question), but some are **distractors**: on topic, without the
answer, and able to push the LLM into a wrong answer (a passage about the 2007 World Cup final when
the question asks about 2011). nDCG cannot tell these two kinds apart.

Trappolini et al. (EACL 2026) measure how distracting each passage is and propose **UDCG**, a metric
that penalises distractors. We use their method to ask: do two common retrieval improvements,
**LLM query expansion (Query2Doc)** and **cross-encoder reranking**, bring more distractors into the
LLM's context? And does a simple, training-free **distractor filter** fix it?

Base paper: [Redefining Retrieval Evaluation in the Era of LLMs](https://arxiv.org/abs/2510.21440),
code and data: [GiovanniTRA/UDCG](https://github.com/GiovanniTRA/UDCG).

## Setup

Python 3.12. Kalp's machine (Apple Silicon Mac) runs everything that needs the Wikipedia index or
the LLM; Zeel's machine (Windows, NVIDIA GPU) runs reranking, evaluation and figures.

```bash
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # everyone
pip install -r requirements-kalp.txt # only on the machine that runs Pyserini (needs Java 21)
```

## Pipeline

| Step | Script | Owner | What it does |
|---|---|---|---|
| 1 | `scripts/01_bm25_baseline.py` | Kalp | Baseline A: BM25 on all 3,610 NQ test questions, compared with published numbers |
| 2 | `scripts/02_sample_questions.py` | Kalp | Picks the 300 questions used in all LLM experiments |
| 3 | `scripts/03_query2doc.py` | Kalp | Query expansion: the LLM writes a pseudo-passage per question |
| 4 | `scripts/04_retrieve.py` | Kalp | BM25 top 50 for plain (S1) and expanded (S2) questions |
| 5 | `scripts/05_rerank.py` | Zeel | Cross-encoder reranking; builds the S1-S4 top-5 contexts |
| 6 | `scripts/06_score_passages.py` | Kalp | Distraction score of every passage (paper's method) |
| 7 | `scripts/07_rag_answers.py` | Kalp | RAG answers for S1-S4, with the filter, and the oracle |
| 8 | `scripts/08_evaluate.py` | Zeel | Tables: nDCG, UDCG, distraction, accuracy, significance tests |
| 9 | `scripts/09_correlation_run.py` | Kalp | Baseline B: LLM answers for the paper's correlation experiment |
| 10 | `scripts/10_correlation_analysis.py` | Zeel | Baseline B: which metric predicts answer correctness |
| 11 | `scripts/11_examples.py` | Kalp | Hand-picked examples |
| 12 | `scripts/12_figures.py` | Zeel | Figures |

Shared code: `src/common.py` (paths, prompts), `src/llm.py` (local LLM), `src/metrics.py`
(all metrics), `src/filter.py` (our distractor filter). Settings: `config.yaml`. Tests: `python -m pytest -q`.

## Results

Filled in at the end of the project.
