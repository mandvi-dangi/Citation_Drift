import csv, json, itertools
from pathlib import Path
import numpy as np
from .data import load_items
from .parse import parse_response
from .grade import grade
from .scoring import kendall_tau, ece

RULES = ["accuracy", "precision", "F", "S1"]

def _scores(c, i, T, lam=1.0):
    c, i = np.asarray(c, float), np.asarray(i, float)
    R = c / T
    P = np.divide(c, c + i, out=np.zeros_like(c), where=(c + i) > 0)
    F = np.divide(2 * P * R, P + R, out=np.zeros_like(c), where=(P + R) > 0)
    return {"accuracy": R, "precision": P, "F": F, "S1": (c - lam * i) / T}

def load_labels(cfg, out_dir):
    items = []
    for p in cfg["datasets"]:
        items += load_items(p)
    if cfg.get("max_items"):
        items = items[: cfg["max_items"]]
    key = [(i["dataset"], i["id"]) for i in items]
    gold = {(i["dataset"], i["id"]): i["answer"] for i in items}
    nopt = {(i["dataset"], i["id"]): len(i["options"]) for i in items}
    labels, conf, correct_attempted, parse_fail = {}, {}, {}, {}
    for spec in cfg["models"]:
        name = spec["name"]; rows = {}
        for line in (Path(out_dir) / "raw" / f"{name}.jsonl").read_text().splitlines():
            r = json.loads(line); rows[(r["dataset"], r["id"])] = r["response"]
        missing = [k for k in key if k not in rows]
        if missing:
            raise ValueError(f"{name}: {len(missing)} items missing; rerun run_models")
        L, cf, ca, pf = [], [], [], 0
        for k in key:
            a, c = parse_response(rows[k], nopt[k])
            pf += a is None
            g = grade(a, gold[k]); L.append(g)
            if g != "N" and c is not None:
                cf.append(c); ca.append(g == "C")
        labels[name], conf[name], correct_attempted[name], parse_fail[name] = L, cf, ca, pf / len(key)
    return key, labels, conf, correct_attempted, parse_fail

def analyze(cfg, out_dir, res_dir):
    res = Path(res_dir); res.mkdir(parents=True, exist_ok=True)
    seed, B = cfg.get("seed", 0), cfg.get("n_boot", 1000)
    key, labels, conf, corr, pfail = load_labels(cfg, out_dir)
    models = list(labels); T = len(key)
    if len(models) < cfg.get("min_models", 6):
        print(f"WARNING: only {len(models)} models; protocol requires >= {cfg.get('min_models', 6)}")
    isC = np.array([[l == "C" for l in labels[m]] for m in models])
    isI = np.array([[l == "I" for l in labels[m]] for m in models])
    isN = np.array([[l == "N" for l in labels[m]] for m in models])
    point = _scores(isC.sum(1), isI.sum(1), T)
    rng = np.random.default_rng(seed)
    pairs = list(itertools.combinations(RULES, 2))
    boots = {p: [] for p in pairs}
    for _ in range(B):
        idx = rng.integers(0, T, T)
        s = _scores(isC[:, idx].sum(1), isI[:, idx].sum(1), T)
        for a, b in pairs:
            boots[(a, b)].append(kendall_tau(list(s[a]), list(s[b])))
    tau = {p: (kendall_tau(list(point[p[0]]), list(point[p[1]])),
               *np.percentile(boots[p], [2.5, 97.5])) for p in pairs}
    # decision rule (frozen in docs/protocol.md): unstable if CI of tau(accuracy,S1) wholly < 0.8;
    # contradicted if CI lower bound >= 0.8 for all rule pairs; otherwise inconclusive.
    lo_all = min(v[1] for v in tau.values())
    hi_main = tau[("accuracy", "S1")][2]
    verdict = ("UNSTABLE (CI of tau(accuracy,S1) entirely below 0.8)" if hi_main < 0.8 else
               "NOT UNSTABLE (CI lower bound >= 0.8 for all rule pairs)" if lo_all >= 0.8 else
               "INCONCLUSIVE")
    ece_v = {m: (ece(conf[m], corr[m]) if conf[m] else float("nan")) for m in models}
    # csv
    with (res / "scores.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["model", *RULES, "abstain_rate", "parse_fail_rate", "ece_attempted"])
        for k, m in enumerate(models):
            w.writerow([m, *[f"{point[r][k]:.4f}" for r in RULES], f"{isN[k].mean():.4f}",
                        f"{pfail[m]:.4f}", f"{ece_v[m]:.4f}"])
    e = lambda s: s.replace("_", "\\_")
    (res / "table_scores.tex").write_text(
        "\\begin{table}[t]\\centering\\caption{Per-model scores under each rule ($T=%d$ items).}\\label{tab:scores}\n"
        "\\begin{tabular}{lrrrrr}\\toprule Model & Acc & Prec & F & $S_1$ & Abstain\\\\\\midrule\n" % T
        + "".join(f"{e(m)} & {point['accuracy'][k]:.3f} & {point['precision'][k]:.3f} & {point['F'][k]:.3f} & "
                  f"{point['S1'][k]:.3f} & {isN[k].mean():.3f}\\\\\n" for k, m in enumerate(models))
        + "\\bottomrule\\end{tabular}\\end{table}\n")
    (res / "table_tau.tex").write_text(
        "\\begin{table}[t]\\centering\\caption{Kendall $\\tau_a$ between rankings (95\\%% item-bootstrap CI, %d resamples).}\\label{tab:tau}\n"
        "\\begin{tabular}{llr}\\toprule Rule pair & $\\tau_a$ & 95\\%% CI\\\\\\midrule\n" % B
        + "".join(f"{a} vs {b} & {v[0]:.3f} & [{v[1]:.3f}, {v[2]:.3f}]\\\\\n" for (a, b), v in tau.items())
        + "\\bottomrule\\end{tabular}\\end{table}\n")
    (res / "table_ece.tex").write_text(
        "\\begin{table}[t]\\centering\\caption{Calibration error of verbalised confidence (attempted items only).}\\label{tab:ece}\n"
        "\\begin{tabular}{lr}\\toprule Model & ECE\\\\\\midrule\n"
        + "".join(f"{e(m)} & {ece_v[m]:.3f}\\\\\n" for m in models)
        + "\\bottomrule\\end{tabular}\\end{table}\n")
    (res / "setup_models.tex").write_text(
        "Models: " + ", ".join(e(s["name"]) + " (" + e(s.get("model", s["name"])) + ")" for s in cfg["models"])
        + ". Greedy decoding, max 32 new tokens, one run per item.\n")
    (res / "setup_datasets.tex").write_text(
        "Datasets: " + ", ".join(e(Path(p).name) for p in cfg["datasets"]) + f"; $T={T}$ items in total.\n")
    (res / "decision.txt").write_text(verdict + "\n")
    print(verdict)
    return {"tau": tau, "verdict": verdict, "models": models, "T": T}
