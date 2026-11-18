#!/usr/bin/env python
"""Query models listed in a config. Usage: python scripts/run_models.py configs/experiment.json [--out results]"""
import argparse, json
from factsens.runner import run_experiment
ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--out", default="results")
a = ap.parse_args()
run_experiment(json.load(open(a.config)), a.out)
