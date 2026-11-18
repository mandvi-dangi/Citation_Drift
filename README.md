# factsens: does the scoring rule change the ranking?

Controlled study of whether model rankings on scientific-factuality QA change under accuracy, attempted-precision,
SimpleQA-style F-score and an error-penalised score, plus calibration of verbalised confidence.
Derived from a literature review of factuality benchmarking (see `docs/review_scope.md`).

**Status:** pipeline and metric code are tested; **no LLM results exist yet.** The synthetic simulation in
`results/table_sim.tex` is a mechanism check, not evidence about real models. Novelty is not claimed (see `docs/protocol.md` §2).

## Layout
```
src/factsens/   scoring.py (metrics) simulate.py data.py prompts.py parse.py grade.py backends.py runner.py analyze.py
scripts/        env_check.py validate_data.py run_models.py analyze.py make_sim_results.py
configs/        experiment.json (edit models + datasets)
data/           put your JSONL item files here (not committed; see data/README.md)
results/        generated tables (*.tex, scores.csv, decision.txt); raw outputs in results/raw/ (git-ignored)
paper/          main.tex (IEEEtran) - loads ../results/*.tex, no hand-typed numbers
docs/           research_decisions.md, protocol.md, gap_analysis.md, review_scope.md, ai_assistance_log.md
tests/          pytest suite (20 tests), fixtures/toy_items.jsonl (plumbing only)
```

## Quick start
```bash
pip install -e ".[dev]"          # add ".[hf]" for local Hugging Face models
python -m pytest -q              # expect: 20 passed
python scripts/env_check.py      # paste output into docs/env_log.txt
python scripts/make_sim_results.py
```

## Running the real experiment
1. Build `data/science_mcq.jsonl` from datasets whose licences you verified; `python scripts/validate_data.py data/science_mcq.jsonl`.
2. Edit `configs/experiment.json`: at least **6 models** (protocol), real model IDs. Backends: `openai_compat`
   (OpenAI, vLLM, Ollama `http://localhost:11434/v1`; key via `api_key_env`) or `hf`. `dummy` is for tests only.
3. Freeze the checklist in `docs/protocol.md` §5 **before** running.
4. `python scripts/run_models.py configs/experiment.json` (resumable), then `python scripts/analyze.py configs/experiment.json`.
5. `cd paper && pdflatex main && pdflatex main`. Write Discussion/Conclusion only after `results/decision.txt` exists.

Decision rule (fixed in advance): rankings are *unstable* if the 95% item-bootstrap CI of Kendall tau(accuracy, S1) lies entirely below 0.8;
*not unstable* if the CI lower bound is >= 0.8 for every rule pair; otherwise inconclusive. Log any later protocol change in `docs/research_decisions.md`.

## Integrity notes
- Real backends never receive the gold answer; `dummy` is the only backend that does.
- Unparseable outputs are graded incorrect and the parse-failure rate is reported.
- Credit the authors of the source review and confirm authorship before submission.
