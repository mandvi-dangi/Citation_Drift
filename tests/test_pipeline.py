import json, shutil
from pathlib import Path
import pytest
from factsens.data import load_items
from factsens.parse import parse_response
from factsens.grade import grade
from factsens.prompts import build_prompt
from factsens.runner import run_experiment
from factsens.analyze import analyze

FIX = Path(__file__).parent / "fixtures" / "toy_items.jsonl"

def test_load_and_prompt():
    items = load_items(FIX)
    assert len(items) == 12
    p = build_prompt(items[0])
    assert "A. Na" in p and "ANSWER:" in p and "NS" in p

def test_load_rejects_bad(tmp_path):
    f = tmp_path / "bad.jsonl"
    f.write_text('{"id":"x","question":"q","options":["a","b"],"answer":"C"}\n')
    with pytest.raises(ValueError): load_items(f)
    f.write_text('{"id":"x","question":"q","options":["a","b"],"answer":"A"}\n{"id":"x","question":"q","options":["a","b"],"answer":"A"}\n')
    with pytest.raises(ValueError): load_items(f)

@pytest.mark.parametrize("text,n,exp", [
    ("ANSWER: B\nCONFIDENCE: 80", 4, ("B", 0.8)),
    ("answer: ns\nconfidence: 0", 4, ("NS", 0.0)),   # case-insensitive
    ("ANSWER: E\nCONFIDENCE: 50", 4, (None, 0.5)),   # letter out of range
    ("I think it is B", 4, (None, None)),
    ("ANSWER: C\nCONFIDENCE: 250", 4, ("C", 1.0)),   # clipped
])
def test_parse(text, n, exp):
    assert parse_response(text, n) == exp

def test_grade():
    assert grade("A", "A") == "C" and grade("B", "A") == "I"
    assert grade("NS", "A") == "N" and grade(None, "A") == "I"

def _cfg(tmp_path, models):
    return {"seed": 0, "n_boot": 100, "min_models": 2, "datasets": [str(FIX)], "models": models}

def test_end_to_end_with_dummy_backends(tmp_path):
    """Plumbing test only: dummy models, NOT results."""
    models = [{"name": "good", "type": "dummy", "skill": 0.95, "abstain": 0.0},
              {"name": "cautious", "type": "dummy", "skill": 0.9, "abstain": 0.5},
              {"name": "weak", "type": "dummy", "skill": 0.3, "abstain": 0.0}]
    cfg = _cfg(tmp_path, models)
    run_experiment(cfg, tmp_path, log=lambda *_: None)
    for m in models:
        lines = (tmp_path / "raw" / f"{m['name']}.jsonl").read_text().splitlines()
        assert len(lines) == 12
        assert "gold" not in lines[0] and '"answer"' not in lines[0]  # gold never stored
    out = analyze(cfg, tmp_path, tmp_path)
    for f in ["scores.csv", "table_scores.tex", "table_tau.tex", "table_ece.tex",
              "setup_models.tex", "setup_datasets.tex", "decision.txt"]:
        assert (tmp_path / f).exists()
    rows = (tmp_path / "scores.csv").read_text().splitlines()
    assert len(rows) == 4
    assert out["T"] == 12 and out["verdict"]

def test_resume_does_not_duplicate(tmp_path):
    cfg = _cfg(tmp_path, [{"name": "m", "type": "dummy", "skill": 0.5}])
    run_experiment(cfg, tmp_path, log=lambda *_: None)
    run_experiment(cfg, tmp_path, log=lambda *_: None)
    assert len((tmp_path / "raw" / "m.jsonl").read_text().splitlines()) == 12

def test_analyze_fails_on_missing_items(tmp_path):
    cfg = _cfg(tmp_path, [{"name": "m", "type": "dummy", "skill": 0.5}])
    run_experiment(cfg, tmp_path, log=lambda *_: None)
    f = tmp_path / "raw" / "m.jsonl"
    f.write_text("\n".join(f.read_text().splitlines()[:5]) + "\n")
    with pytest.raises(ValueError): analyze(cfg, tmp_path, tmp_path)
