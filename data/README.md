# Data (not committed)
Place item files here as JSONL, one object per line:
`{"id": "...", "dataset": "...", "question": "...", "options": ["...", "..."], "answer": "B"}`
Build them yourself from datasets whose licence/access terms you have verified at the official source
(e.g. SciFact, MedQA/PubMedQA subsets, GPQA, SimpleQA: access and terms are UNVERIFIED here).
GPQA is gated: respect its licence and do not commit it. Validate with `python scripts/validate_data.py data/<file>.jsonl`.
Set the same item subset and seed for all models; record the subset rule in docs/research_decisions.md.
