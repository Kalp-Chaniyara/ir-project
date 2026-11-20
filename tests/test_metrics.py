"""Checks for src/metrics.py, using the 2011 Cricket World Cup example from our slides.

Run from the repo root:  python -m pytest -q tests/test_metrics.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metrics import (answer_outcome, contains_answer, distracting_effect, hit_at_k,
                         mcnemar_exact, mrr, ndcg, normalize_answer, precision_at_k, udcg)

GOLD = ["India"]


def test_normalize():
    assert normalize_answer("The  India!") == "india"


def test_contains_answer_whole_words_only():
    assert contains_answer("India won the final", GOLD)
    assert not contains_answer("Indiana Jones", GOLD)


def test_outcomes():
    assert answer_outcome("India", GOLD, context_has_relevant=True) == "correct"
    assert answer_outcome("Australia", GOLD, context_has_relevant=True) == "wrong"
    assert answer_outcome("NO-RESPONSE", GOLD, context_has_relevant=True) == "abstain"
    # right answer but no relevant passage in the context: the LLM answered from memory
    assert answer_outcome("India", GOLD, context_has_relevant=False) == "wrong"


def test_retrieval_metrics():
    rels = [0, 1, 0, 0, 1]
    assert hit_at_k(rels) == 1.0
    assert precision_at_k(rels) == 0.4
    assert mrr(rels) == 0.5
    assert ndcg([1, 1, 0, 0, 0], n_relevant_total=2) == 1.0
    assert 0 < ndcg(rels, n_relevant_total=2) < 1
    assert ndcg([0, 0, 0, 0, 0], n_relevant_total=0) == 0.0


def test_ndcg_cannot_see_distractors():
    # Same relevance labels, so nDCG is identical...
    harmless = dict(rels=[1, 0, 0, 0, 0], p_nrs=[0.0, 0.97, 0.95, 0.96, 0.98])   # recipe-like noise
    harmful = dict(rels=[1, 0, 0, 0, 0], p_nrs=[0.0, 0.15, 0.10, 0.20, 0.12])    # other World Cup finals
    assert ndcg(harmless["rels"], 1) == ndcg(harmful["rels"], 1)
    # ...but UDCG drops when the irrelevant passages are distracting.
    assert udcg(**harmless) > udcg(**harmful)


def test_udcg_matches_paper_formula():
    rels, p_nrs = [1, 0], [0.1, 0.4]
    expected = 1 / (1 + math.exp(-((0.9 + (1 / 3) * -0.6) / 2)))
    assert abs(udcg(rels, p_nrs) - expected) < 1e-12


def test_distracting_effect():
    assert distracting_effect(0.15) == 0.85


def test_mcnemar():
    assert mcnemar_exact([True] * 10, [True] * 10) == 1.0
    assert mcnemar_exact([True] * 20, [False] * 20) < 0.001
