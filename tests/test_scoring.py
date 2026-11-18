import pytest
from factsens.scoring import *

L = list("CCCIIN")  # C=3, I=2, N=1, T=6
def test_basic():
    assert overall_accuracy(L) == pytest.approx(3/6)
    assert attempted_precision(L) == pytest.approx(3/5)
    assert f_score(L) == pytest.approx(2*0.6*0.5/1.1)
    assert penalised_score(L) == pytest.approx((3-2)/6)

def test_abstain_never_hurts_precision():
    assert attempted_precision(list("CCN")) == 1.0
    assert overall_accuracy(list("CCN")) == pytest.approx(2/3)

def test_all_abstain_edge():
    assert f_score(list("NNN")) == 0.0 and attempted_precision(list("NNN")) == 0.0

def test_bad_label():
    with pytest.raises(ValueError): overall_accuracy(["X"])

def test_factscore():
    assert factscore([True, True, False, True]) == 0.75
    with pytest.raises(ValueError): factscore([])

def test_ece():
    assert ece([0.5]*4, [True, True, False, False]) == pytest.approx(0.0)
    assert ece([1.0]*4, [True, False, False, False]) == pytest.approx(0.75)

def test_kendall():
    assert kendall_tau([1,2,3],[1,2,3]) == 1.0
    assert kendall_tau([1,2,3],[3,2,1]) == -1.0

def test_ranking_can_flip():
    # hand-built fixture (NOT data): guesser vs cautious model
    guesser  = list("C"*6 + "I"*4)
    cautious = list("C"*5 + "N"*5)
    rules = {"acc": overall_accuracy, "net": penalised_score}
    _, s, t = ranking_stability({"guesser": guesser, "cautious": cautious}, rules)
    assert s["acc"][0] > s["acc"][1]
    assert s["net"][0] < s["net"][1]
    assert t[("acc","net")] == -1.0

def test_simulation_no_abstention_rules_agree():
    # with nobody abstaining S_1 = 2*acc-1 is monotone in accuracy, so S_1 ranks exactly like accuracy
    import numpy as np
    from factsens.simulate import population, tau_pair
    pop = population(8, 300, 0.0, np.random.default_rng(1))
    assert tau_pair(pop, overall_accuracy, penalised_score) == tau_pair(pop, overall_accuracy, overall_accuracy)
