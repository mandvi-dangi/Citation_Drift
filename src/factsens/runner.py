import json
from pathlib import Path
from .data import load_items
from .prompts import build_prompt, prompt_hash
from .backends import make_backend

def run_experiment(cfg, out_dir, log=print):
    """Query every model on every item; append raw outputs to out_dir/raw/<model>.jsonl (resumable)."""
    raw = Path(out_dir) / "raw"; raw.mkdir(parents=True, exist_ok=True)
    items = []
    for p in cfg["datasets"]:
        items += load_items(p)
    ids = [(i["dataset"], i["id"]) for i in items]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate (dataset,id) across datasets")
    if cfg.get("max_items"):
        items = items[: cfg["max_items"]]
    for spec in cfg["models"]:
        name = spec["name"]
        f = raw / f"{name}.jsonl"
        done = set()
        if f.exists():
            for line in f.read_text().splitlines():
                r = json.loads(line); done.add((r["dataset"], r["id"]))
        be = make_backend(spec)
        with f.open("a", encoding="utf-8") as fh:
            for it in items:
                if (it["dataset"], it["id"]) in done:
                    continue
                prompt = build_prompt(it)
                resp = be.generate(prompt, it if be.needs_item else None)
                fh.write(json.dumps({"model": name, "dataset": it["dataset"], "id": it["id"],
                                     "prompt_hash": prompt_hash(prompt), "response": resp}) + "\n")
                fh.flush()
        log(f"{name}: {len(items)} items done")
    return items
