# AI-assistance and debugging log
| Date | Tool | What it did | What the author verified |
|------|------|-------------|--------------------------|
| 2026-11-17/18 | Claude | Drafted gap analysis, protocol, code scaffolding, paper skeleton | Authors must re-check every claim against original papers and run all code themselves |
| 2026-11-18 | Claude | Bug found and fixed by tests: numpy bool subtraction in Kendall tau; regex case-sensitivity for CONFIDENCE | Fix verified by pytest (20 passed) |
Add one row per debugging episode (prompt 11): code, actual traceback, fix, rerun needed?
