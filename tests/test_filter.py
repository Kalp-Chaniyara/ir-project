"""Checks for the distractor filter. Run:  python -m pytest -q tests/test_filter.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.filter import majority_filter


def test_world_cup_example():
    # India, India, Australia (2007 final), NO-RESPONSE, Pakistan
    r = majority_filter(["India", "india.", "Australia", "NO-RESPONSE", "Pakistan"])
    assert r["keep"] == [0, 1]
    assert r["majority"] == "india"


def test_tie_goes_to_highest_ranked_passage():
    r = majority_filter(["Australia", "India", "NO-RESPONSE"])
    assert r["keep"] == [0]
    assert r["reason"] == "tie broken by rank"


def test_all_abstain_keeps_everything():
    r = majority_filter(["NO-RESPONSE", "no response", ""])
    assert r["keep"] == [0, 1, 2]
    assert r["majority"] is None


def test_known_failure_case():
    # If most passages are distractors agreeing on the same wrong answer, the filter keeps them.
    r = majority_filter(["Australia", "Australia", "India"])
    assert r["keep"] == [0, 1]
