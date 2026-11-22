"""Query expansion with Query2Doc (Wang et al., EMNLP 2023).

For each question, the LLM writes a short passage that it thinks answers the question
(a "pseudo-document"). The expanded BM25 query is the question repeated 5 times plus that
passage, as in the Query2Doc paper. Repeating the question keeps it from being drowned out
by the longer generated text.

Run (Kalp, Mac):  python scripts/03_query2doc.py
Time: about 15 minutes for 300 questions. Safe to stop and re-run: finished questions are skipped.
"""
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PATHS, ROOT, load_config, read_jsonl  # noqa: E402

PROMPT = ("Write a short Wikipedia-style passage (about 100 words) that answers the question below. "
          "Write only the passage.\nQuestion: {question}")


def main():
    cfg = load_config()
    from src.llm import LocalLLM

    questions = read_jsonl(PATHS["sample"])
    out_path = PATHS["q2d"]
    done = {r["qid"] for r in read_jsonl(out_path)} if out_path.exists() else set()
    todo = [q for q in questions if q["qid"] not in done]
    print(f"{len(done)} already done, {len(todo)} to go")
    if not todo:
        return

    llm = LocalLLM(cfg["models"]["llm"], cfg["llm"]["dtype"])
    n = cfg["query2doc"]["repeat_query"]
    import json
    with open(out_path, "a", encoding="utf-8") as f:
        for q in tqdm(todo, desc="Query2Doc"):
            pseudo = llm.free_text(PROMPT.format(question=q["question"]), cfg["query2doc"]["max_new_tokens"])
            pseudo = " ".join(pseudo.split())
            expanded = " ".join([q["question"]] * n + [pseudo])
            f.write(json.dumps({"qid": q["qid"], "question": q["question"], "pseudo_doc": pseudo,
                                "expanded_query": expanded}, ensure_ascii=False) + "\n")
            f.flush()

    rows = read_jsonl(out_path)
    print(f"\nSaved {len(rows)} expansions to {out_path.relative_to(ROOT)}. Two examples:")
    for r in rows[:2]:
        print(f"\nQ: {r['question']}\nPseudo-doc: {r['pseudo_doc'][:300]}")


if __name__ == "__main__":
    main()
