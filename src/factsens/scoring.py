"""Scoring rules for the scoring-rule sensitivity study (RQ1).
Definitions follow the review's Eq.(1)-(2) [FActScore; SimpleQA F-score].
Outcome labels per item: 'C' correct, 'I' incorrect, 'N' not attempted.
"""
from __future__ import annotations
import math
from typing import Sequence

def _counts(labels: Sequence[str]):
    c = sum(l == "C" for l in labels); i = sum(l == "I" for l in labels)
    n = sum(l == "N" for l in labels)
    if c + i + n != len(labels) or not labels:
        raise ValueError("labels must be a non-empty sequence over {'C','I','N'}")
    return c, i, n

def overall_accuracy(labels):            # R = C/T (review Eq.2)
    c, i, n = _counts(labels); return c / len(labels)

def attempted_precision(labels):         # P = C/(C+I)
    c, i, _ = _counts(labels); return c / (c + i) if (c + i) else 0.0

def f_score(labels):                     # F = 2PR/(P+R)
    r, p = overall_accuracy(labels), attempted_precision(labels)
    return 2 * p * r / (p + r) if (p + r) else 0.0

def penalised_score(labels, wrong_penalty=1.0):
    """Net score: +1 correct, -wrong_penalty incorrect, 0 abstain, per item."""
    c, i, _ = _counts(labels); return (c - wrong_penalty * i) / len(labels)

def factscore(supported: Sequence[bool]):  # review Eq.(1) for one response
    if not supported: raise ValueError("no atomic facts")
    return sum(bool(s) for s in supported) / len(supported)

def ece(conf: Sequence[float], correct: Sequence[bool], n_bins=10):
    """Expected calibration error, equal-width bins on [0,1]."""
    if len(conf) != len(correct) or not conf: raise ValueError("bad input")
    tot, err = len(conf), 0.0
    for b in range(n_bins):
        lo, hi = b / n_bins, (b + 1) / n_bins
        idx = [k for k, c in enumerate(conf) if (lo <= c < hi) or (b == n_bins - 1 and c == 1.0)]
        if not idx: continue
        acc = sum(correct[k] for k in idx) / len(idx)
        avg = sum(conf[k] for k in idx) / len(idx)
        err += len(idx) / tot * abs(acc - avg)
    return err

def kendall_tau(a: Sequence[float], b: Sequence[float]):
    """Kendall tau-a between two score vectors over the same models."""
    n = len(a)
    if n != len(b) or n < 2: raise ValueError("bad input")
    s = 0
    for x in range(n):
        for y in range(x + 1, n):
            p = (a[x]-a[y])*(b[x]-b[y])
            s += int(p > 0) - int(p < 0)
    return s / (n*(n-1)/2)

def ranking_stability(per_model_labels: dict, rules: dict):
    models = list(per_model_labels)
    scores = {r: [f(per_model_labels[m]) for m in models] for r, f in rules.items()}
    names = list(rules); taus = {}
    for x in range(len(names)):
        for y in range(x+1, len(names)):
            taus[(names[x], names[y])] = kendall_tau(scores[names[x]], scores[names[y]])
    return models, scores, taus
