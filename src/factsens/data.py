"""Item loading/validation. Item JSONL schema (one object per line):
{"id": str, "dataset": str, "question": str, "options": [str,...], "answer": "A"}
`answer` is the letter of the gold option. Data are NOT committed; see data/README.md."""
import json
from pathlib import Path
LETTERS = "ABCDEFGHIJ"

def load_items(path):
    items, seen = [], set()
    for ln, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        it = json.loads(line)
        for k in ("id", "question", "options", "answer"):
            if k not in it:
                raise ValueError(f"{path}:{ln} missing field '{k}'")
        if it["id"] in seen:
            raise ValueError(f"{path}:{ln} duplicate id {it['id']}")
        seen.add(it["id"])
        n = len(it["options"])
        if not 2 <= n <= len(LETTERS):
            raise ValueError(f"{path}:{ln} need 2-{len(LETTERS)} options")
        if it["answer"] not in LETTERS[:n]:
            raise ValueError(f"{path}:{ln} answer '{it['answer']}' not among options")
        it.setdefault("dataset", Path(path).stem)
        items.append(it)
    if not items:
        raise ValueError(f"{path}: no items")
    return items
