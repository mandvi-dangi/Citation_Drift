# research_decisions.md  (portable decision log)
Labels: VERIFIED = seen in a file/log you supplied; INFERRED = my reasoning; UNKNOWN = needs your input.

| ID | Date | Decision | Reason | Evidence | Next action |
|----|------|----------|--------|----------|-------------|
| D-001 | 2026-11-17 | Source = "Benchmarking Factual Accuracy of LLMs Across Scientific Domains" (review, 12 pp) | Provided PDF | Updated_Paper.pdf (VERIFIED) | Confirm authorship/consent (see D-009) |
| D-002 | 2026-11-17 | Gaps extracted from review's own §5.3, §5.4, §7, §8 | Prompt 02 | gap_analysis.md | You check each against original papers |
| D-003 | 2026-11-17 | Candidate study type = (B) controlled comparison | Smallest working baseline; no training; cheap | gap_analysis.md §3 | You confirm |
| D-004 | 2026-11-17 | Primary question = scoring-rule sensitivity of model rankings (G1) | Review §8 says reward-for-guessing is non-uniform; testable with outputs only | Review lines ~513-520 | Freeze after you confirm models/datasets |
| D-005 | 2026-11-17 | Metric code written + unit-tested before any model is run | Avoid post-hoc metric choice | tests/ : 8 passed (VERIFIED, run in this session) | Run on your machine |
| D-006 | 2026-11-17 | NO results, tables or numbers in the paper until real runs exist | Integrity; your standing rule | - | Run experiments |
| D-007 | 2026-11-17 | Network sandbox here cannot reach HuggingFace/dataset hosts or LLM APIs without your key | Allow-list of sandbox (VERIFIED from environment config) | - | Run model inference in Colab/local/institutional GPU |
| D-008 | 2026-11-17 | Novelty NOT claimed | Prompt 04 requires separate literature search | - | Run search strings in protocol.md §2 |
| D-009 | 2026-11-17 | Authorship: PDF names Manju Kumari (IIIT-A). Implementation paper must credit/obtain agreement of the review's author(s) and cite it | Integrity | PDF title page | You confirm who the authors are |

## UNKNOWN (blocking)
hardware; weeks available; which models; target venue; whether API keys are available; which datasets you can legally download.

| D-010 | 2026-11-18 | Repository `factsens` created: tested metrics, parser, grader, runner (OpenAI-compatible / HF backends), analysis with bootstrap and decision rule | Reproducible pipeline | `python -m pytest` -> 20 passed (VERIFIED in sandbox) | Run on real models |
| D-011 | 2026-11-18 | Unparseable output is graded Incorrect (not abstention); parse-fail rate is reported | A format failure is not a calibrated abstention | src/factsens/grade.py | Review after seeing parse-fail rates only if logged as an amendment |
| D-012 | 2026-11-18 | Synthetic simulation included, labelled as not LLM evidence | Shows mechanism only | results/table_sim.tex | Keep separate from LLM results |
