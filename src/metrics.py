"""All evaluation metrics in one place.

Retrieval metrics look at relevance labels only (does a passage contain a gold answer?).
UDCG also uses how strongly the LLM reacts to each passage (P_nr, the probability that
the LLM's first token is NO-RESPONSE when it sees only that passage).

This file has no dependencies beyond numpy and scipy, so it runs on any laptop.
"""
from __future__ import annotations

import math
import re
import string

import numpy as np


# ---------------------------------------------------------------- answer matching

def normalize_answer(s: str) -> str:
    """Standard SQuAD/NQ normalisation: lowercase, drop punctuation and articles, squash spaces."""
    s = s.lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def contains_answer(text: str, gold_answers: list[str]) -> bool:
    """True if any gold answer appears in `text` as a whole run of words.
    'India' matches 'india won', but 'Ind' does not match 'india'."""
    words = normalize_answer(text).split()
    for gold in gold_answers:
        g = normalize_answer(gold).split()
        if not g:
            continue
        for i in range(len(words) - len(g) + 1):
            if words[i:i + len(g)] == g:
                return True
    return False


def is_abstain(answer: str) -> bool:
    a = answer.strip().lower()
    return a == "" or "no-response" in a or "no response" in a


def answer_outcome(answer: str, gold_answers: list[str], context_has_relevant: bool) -> str:
    """'abstain', 'correct' or 'wrong'.

    Following the paper, an answer only counts as correct if the context really contained a
    relevant passage, so the LLM cannot score from its own memory.
    """
    if is_abstain(answer):
        return "abstain"
    if context_has_relevant and contains_answer(answer, gold_answers):
        return "correct"
    return "wrong"


OUTCOME_SCORE = {"correct": 2, "abstain": 1, "wrong": 0}  # the paper's ideal ranking


# ---------------------------------------------------------------- retrieval metrics
# `rels` is a list of 0/1 relevance labels in ranked order, e.g. [0, 1, 0, 0, 1].

def hit_at_k(rels: list[int]) -> float:
    return 1.0 if any(rels) else 0.0


def precision_at_k(rels: list[int]) -> float:
    return sum(rels) / len(rels) if rels else 0.0


def mrr(rels: list[int]) -> float:
    for i, r in enumerate(rels, 1):
        if r:
            return 1.0 / i
    return 0.0


def dcg(rels: list[int]) -> float:
    return sum(r / math.log2(i + 1) for i, r in enumerate(rels, 1))


def ndcg(rels: list[int], n_relevant_total: int) -> float:
    """Binary nDCG@k with k = len(rels).

    The ideal list puts min(k, n_relevant_total) relevant passages at the top.
    n_relevant_total = relevant passages known for this question across all pipelines,
    so every pipeline is divided by the same ideal and the comparison is fair.
    """
    k = len(rels)
    n_ideal = min(k, n_relevant_total)
    if n_ideal == 0:
        return 0.0
    return dcg(rels) / dcg([1] * n_ideal)


# ---------------------------------------------------------------- distraction and UDCG

def distracting_effect(p_nr: float) -> float:
    """DE = 1 - P(NO-RESPONSE). Only meaningful for irrelevant passages:
    0 = the LLM ignores it, 1 = the LLM always tries to answer from it."""
    return 1.0 - p_nr


def utility(is_relevant: bool, p_nr: float) -> float:
    """Paper's passage utility: +(1 - P_nr) if relevant, -(1 - P_nr) if irrelevant."""
    u = 1.0 - p_nr
    return u if is_relevant else -u


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def udcg(rels: list[int], p_nrs: list[float], gamma: float = 1 / 3) -> float:
    """UDCG(q, C) = sigmoid( (1/k) * sum(positive utilities) + (gamma/k) * sum(negative utilities) ).
    Same formula as the paper and its code (compute_udcg_scores.py). No position discount."""
    k = len(rels)
    if k == 0:
        return sigmoid(0.0)
    pos = sum(utility(True, p) for r, p in zip(rels, p_nrs) if r)
    neg = sum(utility(False, p) for r, p in zip(rels, p_nrs) if not r)
    return sigmoid((pos + gamma * neg) / k)


# ---------------------------------------------------------------- significance tests

def mcnemar_exact(correct_a: list[bool], correct_b: list[bool]) -> float:
    """Exact McNemar test (two-sided binomial test on the questions where A and B disagree)."""
    from scipy.stats import binomtest
    b = sum(1 for x, y in zip(correct_a, correct_b) if x and not y)
    c = sum(1 for x, y in zip(correct_a, correct_b) if y and not x)
    if b + c == 0:
        return 1.0
    return float(binomtest(b, b + c, 0.5).pvalue)


def wilcoxon_p(a: list[float], b: list[float]) -> float:
    """Paired Wilcoxon signed-rank test; 1.0 when the two lists are identical."""
    from scipy.stats import wilcoxon
    diffs = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    if np.allclose(diffs, 0):
        return 1.0
    return float(wilcoxon(a, b).pvalue)
