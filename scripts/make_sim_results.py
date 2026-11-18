#!/usr/bin/env python
"""Synthetic simulation table (NOT LLM data) -> results/table_sim.tex"""
import os
from factsens.simulate import run
rows = run()
os.makedirs("results", exist_ok=True)
with open("results/table_sim.tex", "w") as f:
    f.write("\\begin{table}[t]\\centering\\caption{Synthetic simulation (not LLM data): agreement between accuracy ranking and rankings under $S_1$ and F over 200 random populations of 8 models, 500 items, seed 0. Spread is the upper bound of the uniform abstention-threshold distribution.}\\label{tab:sim}\n")
    f.write("\\begin{tabular}{lrrrrr}\\toprule Spread & mean $\\tau_{S_1}$ & 5th pct $\\tau_{S_1}$ & frac $\\tau_{S_1}<0.8$ & mean $\\tau_F$ & frac $\\tau_F<0.8$\\\\\\midrule\n")
    for r in rows:
        f.write(f"{r['spread']:.1f} & {r['mean_tau_S1']:.3f} & {r['p05_tau_S1']:.3f} & {r['frac_below_08_S1']:.2f} & {r['mean_tau_F']:.3f} & {r['frac_below_08_F']:.2f}\\\\\n")
    f.write("\\bottomrule\\end{tabular}\\end{table}\n")
for r in rows: print(r)
