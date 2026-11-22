"""BM25 retrieval for the plain questions (S1) and the Query2Doc-expanded questions (S2).

Keeps the top 50 passages per question, with their text and a has_answer label
(does the passage contain a gold answer?), using Pyserini's own DPR answer check.
Zeel's reranker (scripts/05_rerank.py) reads these two files.

Run (Kalp, Mac):  python scripts/04_retrieve.py
Time: a few minutes.
"""
import json
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, read_jsonl, write_jsonl  # noqa: E402


def split_contents(raw: str):
    """DPR index stores '"Title"\\npassage text'."""
    contents = json.loads(raw)["contents"]
    title, _, text = contents.partition("\n")
    return title.strip().strip('"'), text.strip()


def main():
    from pyserini.eval.evaluate_dpr_retrieval import SimpleTokenizer, has_answers
    from pyserini.search.lucene import LuceneSearcher

    cfg = load_config()
    depth = cfg["retrieval"]["depth"]
    questions = read_jsonl(PATHS["sample"])
    q2d = {r["qid"]: r["expanded_query"] for r in read_jsonl(PATHS["q2d"])}
    missing = [q["qid"] for q in questions if q["qid"] not in q2d]
    if missing:
        sys.exit(f"Query2Doc output is missing {len(missing)} questions. Run scripts/03_query2doc.py first.")

    searcher = LuceneSearcher.from_prebuilt_index(cfg["data"]["index"])
    tokenizer = SimpleTokenizer()
    qids = [q["qid"] for q in questions]
    query_sets = {
        "S1": [q["question"] for q in questions],
        "S2": [q2d[q["qid"]] for q in questions],
    }

    for setup, queries in query_sets.items():
        hits = searcher.batch_search(queries, qids, k=depth, threads=cfg["retrieval"]["threads"])
        rows = []
        for q in tqdm(questions, desc=f"{setup} fetch passages"):
            passages = []
            for rank, h in enumerate(hits[q["qid"]], 1):
                title, text = split_contents(searcher.doc(h.docid).raw())
                passages.append({"pid": h.docid, "rank": rank, "score": round(float(h.score), 4),
                                 "title": title, "text": text,
                                 "has_answer": bool(has_answers(text, q["answers"], tokenizer, False))})
            rows.append({"qid": q["qid"], "question": q["question"], "answers": q["answers"], "hits": passages})
        out = PATHS["runs"] / f"{setup}_top{depth}.jsonl"
        write_jsonl(rows, out)

        def hit_at(k):
            return 100 * sum(any(p["has_answer"] for p in r["hits"][:k]) for r in rows) / len(rows)
        print(f"{setup}: saved {out.relative_to(ROOT)} | Hit@5 {hit_at(5):.1f}  Hit@20 {hit_at(20):.1f}  "
              f"Hit@50 {hit_at(50):.1f}")


if __name__ == "__main__":
    main()
