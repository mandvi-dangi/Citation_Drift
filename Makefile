.PHONY: install test sim run analyze paper
install:
	pip install -e ".[dev]"
test:
	python -m pytest -q
sim:
	python scripts/make_sim_results.py
run:
	python scripts/run_models.py configs/experiment.json
analyze:
	python scripts/analyze.py configs/experiment.json
paper:
	cd paper && pdflatex main && pdflatex main
