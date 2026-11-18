# Prompt 02: Gap matrix  (source evidence -> question -> experiment)
"Reported" = the review itself says it. "Inferred" = my extrapolation. Novelty is NOT claimed.

| # | Gap | Where in review | Reported / Inferred | Testable question | Evidence that would test it | Feasibility |
|---|-----|-----------------|---------------------|-------------------|-----------------------------|-------------|
| G1 | No uniform reward for confident guessing vs abstaining; few calibration curves | §5.3; §8 para 2 (lines ~513-521) | Reported | Do model rankings change under accuracy vs F-score vs error-penalised scoring? | Same model outputs scored by 3-4 rules; Kendall tau + bootstrap CI | HIGH (output-only) |
| G2 | MCQ can be solved by elimination; high MCQ != good generation | §5.1, §7.4 (lines ~493-497) | Reported (cites [6],[11]) | How large is the MCQ-vs-open-answer accuracy gap on the same facts? | Paired items, options hidden vs shown | MEDIUM (needs open-answer grader) |
| G3 | Retrieval confounds parametric-knowledge measurement | §5.4; §8 last para | Reported | How much of a score is retrieval vs parametric? | Same items with/without fixed retrieved context | MEDIUM |
| G4 | Static benchmarks, contamination | §7.1, §7.5, §8 para 1 | Reported | Does accuracy drop on post-cutoff items? | Time-split items; model cutoff dates | LOW (needs new data, cutoff facts) |
| G5 | English-only, text-only | §8 para 3 | Reported | Multilingual/multimodal gap | Translated/figure items | LOW |

Top 3 by significance x resources x feasibility: **G1 > G2 > G3**.

## Claims in the review to verify against originals before reusing (do NOT repeat unchecked)
1. §5.4 "SimpleQA Verified shows near perfect performance with tools": no reference for SimpleQA Verified in the list; UNKNOWN.
2. Table 2 ChemBench "o1-preview about 2x best human": verify in Mirza et al. [6].
3. §6.2 "no correlation between molecular complexity and performance -> memorisation": the inference is the review's; verify.
4. §6.4 SciFact-Open "~500,000 abstracts": verify.
5. TruthfulQA/ChemBench/TruthfulQA "confidence did not match accuracy" (§5.3): verify each separately.
## Editorial defects in the source (fix before it is cited or built on)
- §6.5 sentence truncated ("error rate below 2", % and rest missing).
- §9 calls Eq.(2) "adversarial factuality"; Eq.(2) is the SimpleQA F-score.
- §4.2 "despite achieving a high score on FActScore": FActScore is a metric, not a model result.
- §5.1/§5.2 use "Our design" / "We have shown" for results of GPQA and FActScore authors.

# Prompt 03: literature -> executable experiment (mapping)
| Method (review ref) | Algorithm | Data | Code/weights access | Metric | Limitation | Compute |
|---|---|---|---|---|---|---|
| SimpleQA scoring [12] | C/I/N grading, F-score | SimpleQA | UNKNOWN: verify official repo & license | R,P,F | single answer, ~3% label error (review) | scoring only |
| ChemBench-style confidence [6] | verbalised confidence vs correctness | ChemBench | UNKNOWN: verify | accuracy vs confidence | self-reported confidence | low |
| FActScore [5] | atomic-fact precision | needs knowledge source + LLM | UNKNOWN: verify | Eq.1 | needs retriever + judge LLM | medium |

Studies: (A) reproduce SimpleQA scoring + extend to science MCQ; (B) **controlled comparison of scoring rules on identical outputs (recommended)**; (C) targeted modification: abstention-aware prompting.
Smallest baseline for B: >=3 (ideally 6+) open-weight models x 1-2 science datasets x 4 scoring rules.
You must personally verify before coding: dataset licences/gating (GPQA is gated; check terms), official split, model names/versions you will use, grader choice.
