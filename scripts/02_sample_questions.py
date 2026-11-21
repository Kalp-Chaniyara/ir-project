"""Pick the 300 questions used in every LLM experiment (fixed seed, so the choice is reproducible).

Run (Kalp, Mac):  python scripts/02_sample_questions.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, parse_answers, write_jsonl  # noqa: E402


def main():
    from pyserini.search import get_topics

    cfg = load_config()
    topics = get_topics(cfg["data"]["topics"])
    qids = sorted(topics)
    print(f"Loaded {len(qids)} questions from {cfg['data']['topics']}")

    chosen = sorted(random.Random(cfg["seed"]).sample(qids, cfg["data"]["n_questions"]))
    rows = [{"qid": str(q), "question": topics[q]["title"], "answers": parse_answers(topics[q]["answers"])}
            for q in chosen]
    write_jsonl(rows, PATHS["sample"])

    print(f"Saved {len(rows)} questions to {PATHS['sample'].relative_to(ROOT)}")
    for r in rows[:3]:
        print(f"  {r['qid']}: {r['question']}  ->  {r['answers']}")


if __name__ == "__main__":
    main()
