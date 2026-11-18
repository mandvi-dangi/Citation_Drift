"""Synthetic simulation of scoring-rule sensitivity (NOT LLM data).
Mechanism check: how often do rankings differ between accuracy and the
error-penalised score when models differ in ability AND abstention threshold?
Model m: ability theta_m; item difficulty d ~ N(0,1); P(correct)=sigmoid(theta-d).
Model confidence = P(correct)+N(0,noise); abstains if confidence < thr_m.
"""
import numpy as np
from .scoring import overall_accuracy, penalised_score, f_score, attempted_precision, kendall_tau

def _labels(theta, thr, d, rng, noise=0.1):
    p = 1/(1+np.exp(-(theta-d)))
    correct = rng.random(len(d)) < p
    conf = p + rng.normal(0, noise, len(d))
    abst = (conf < thr) if thr > 0 else np.zeros(len(d), bool)  # thr=0 means never abstain
    return ["N" if a else ("C" if c else "I") for a, c in zip(abst, correct)]

def population(n_models, n_items, thr_spread, rng):
    d = rng.normal(0, 1, n_items)
    thetas = rng.uniform(-0.5, 1.5, n_models)
    thrs = np.clip(rng.uniform(0, thr_spread, n_models), 0, 1)
    return {f"m{k}": _labels(thetas[k], thrs[k], d, rng) for k in range(n_models)}

def tau_pair(pop, f1, f2):
    ms = list(pop)
    return kendall_tau([f1(pop[m]) for m in ms], [f2(pop[m]) for m in ms])

def run(thr_spreads=(0.0, 0.2, 0.4, 0.6), n_pop=200, n_models=8, n_items=500, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for s in thr_spreads:
        taus = {"acc_vs_S1": [], "acc_vs_F": []}
        for _ in range(n_pop):
            pop = population(n_models, n_items, s, rng)
            taus["acc_vs_S1"].append(tau_pair(pop, overall_accuracy, penalised_score))
            taus["acc_vs_F"].append(tau_pair(pop, overall_accuracy, f_score))
        t = np.array(taus["acc_vs_S1"]); u = np.array(taus["acc_vs_F"])
        rows.append(dict(spread=s, mean_tau_S1=t.mean(), p05_tau_S1=np.percentile(t, 5),
                         frac_below_08_S1=(t < 0.8).mean(), mean_tau_F=u.mean(),
                         frac_below_08_F=(u < 0.8).mean()))
    return rows
