#!/usr/bin/env python
"""Grade raw outputs, compute scores, tau+bootstrap, ECE, write results/*.tex, scores.csv, decision.txt."""
import argparse, json
from factsens.analyze import analyze
ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--out", default="results")
a = ap.parse_args()
analyze(json.load(open(a.config)), a.out, a.out)
