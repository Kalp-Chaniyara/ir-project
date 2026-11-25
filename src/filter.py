"""Our improvement: a training-free distractor filter.

Idea: before the final answer, the LLM has already answered the question from each passage
on its own (we need that anyway to measure distraction). Relevant passages tend to agree on
the right answer. Distractors point somewhere else ("Australia" from the 2007 final).
So we keep only the passages that agree with the most common answer.

The filter never looks at the gold answer, so a real system could use it.
"""
from __future__ import annotations

from collections import Counter

from src.metrics import is_abstain, normalize_answer


def majority_filter(single_answers: list[str]) -> dict:
    """Decide which passages to keep.

    single_answers: the LLM's answer from each passage alone, in rank order.
    Returns {"keep": [indices], "majority": normalised answer or None, "reason": str}.

    Rules:
      1. Ignore NO-RESPONSE answers.
      2. Normalise the rest (lowercase, no punctuation or articles).
      3. The most common answer wins. Ties go to the answer of the highest-ranked passage.
      4. Keep only the passages that gave the winning answer.
      5. If every passage abstained, keep everything (nothing to vote on).
    """
    normalised = [None if is_abstain(a) else normalize_answer(a) for a in single_answers]
    votes = [a for a in normalised if a]
    if not votes:
        return {"keep": list(range(len(single_answers))), "majority": None, "reason": "all abstained"}

    counts = Counter(votes)
    best = max(counts.values())
    tied = {a for a, c in counts.items() if c == best}
    majority = next(a for a in normalised if a in tied)      # first in rank order breaks ties
    keep = [i for i, a in enumerate(normalised) if a == majority]
    reason = "majority" if len(tied) == 1 else "tie broken by rank"
    return {"keep": keep, "majority": majority, "reason": reason}
