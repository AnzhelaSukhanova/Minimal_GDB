from pyformlang.finite_automaton import EpsilonNFA, State, Symbol
from main import *

def test_sa():
    cfg = scan_cfg("syntax")
    cfg.variables.add(Variable("Name"))
    add_letter_prod(cfg, Variable('Name'))
    add_digit_prod(cfg, Variable('Name'))
    cfg_in_cnf = to_cnf(cfg)

    assert syn_analyzer(cfg_in_cnf, "tests/prog0")
    assert syn_analyzer(cfg_in_cnf, "tests/prog1")


def test_cfpq():
    graph = Graph()
    graph.scan("tests/graph2.txt")
    cfg = scan_cfg("tests/gram1.txt")
    cfg_in_cnf = to_cnf(cfg)
    hell = cfpq_hellings(graph, cfg_in_cnf)
    mul = cfpq_MxM(graph, cfg_in_cnf)
    rec_auto, heads = build_rec_automaton(cfg)
    tensor = cfpq_tensor(graph, cfg, rec_auto, heads)
    assert hell.iseq(mul)
    assert hell.iseq(tensor)

    cfg = scan_cfg("tests/gram0.txt")
    cfg_in_cnf = to_cnf(cfg)
    hell = cfpq_hellings(graph, cfg_in_cnf)
    mul = cfpq_MxM(graph, cfg_in_cnf)
    rec_auto, heads = build_rec_automaton(cfg)
    tensor = cfpq_tensor(graph, cfg, rec_auto, heads)
    assert hell.iseq(Matrix.sparse(BOOL, 3, 3).full(True))
    assert hell.iseq(mul)
    assert hell.iseq(tensor)

    graph.scan("tests/graph_empty.txt")
    hell = cfpq_hellings(graph, cfg_in_cnf)
    mul = cfpq_MxM(graph, cfg_in_cnf)
    tensor = cfpq_tensor(graph, cfg, rec_auto, heads)
    assert not hell
    assert hell == mul == tensor

    graph.scan("tests/graph_loop.txt")
    hell = cfpq_hellings(graph, cfg_in_cnf)
    mul = cfpq_MxM(graph, cfg_in_cnf)
    tensor = cfpq_tensor(graph, cfg, rec_auto, heads)
    assert hell.nvals == 1
    assert hell.iseq(mul)
    assert hell.iseq(tensor)

    graph.scan("tests/graph0.txt")
    cfg_in_crf = to_crf(cfg)
    hell = cfpq_hellings(graph, cfg_in_crf)
    mul = cfpq_MxM(graph, cfg_in_crf)
    tensor = cfpq_tensor(graph, cfg_in_crf, rec_auto, heads)
    assert hell.nvals == 0
    assert hell.nvals == mul.nvals == tensor.nvals


def test_cyk():
    cfg = scan_cfg("tests/gram0.txt")
    cfg_in_cnf = to_cnf(cfg)
    assert cyk(cfg_in_cnf, "5 5 5 5 5 5")
    assert not cyk(cfg_in_cnf, "1 2 3 4 5")
    assert cyk(cfg_in_cnf, "4 4 5")
    assert not cyk(cfg_in_cnf, "55")
    assert cyk(cfg_in_cnf, " ")

    cfg = scan_cfg("tests/gram1.txt")
    cfg_in_cnf = to_cnf(cfg)
    assert cyk(cfg_in_cnf, "5 5 5 5 5 5")
    assert not cyk(cfg_in_cnf, "1 2 3 4 5")
    assert not cyk(cfg_in_cnf, "4 4 5")
    assert not cyk(cfg_in_cnf, "55")
    assert not cyk(cfg_in_cnf, " ")


def test_graph_inter():
    graph = Graph()
    automaton = Graph()
    res = Graph()

    graph.scan("tests/graph0.txt")
    automaton.scan_regexp("tests/reg0.txt")
    res.intersection(graph, automaton)
    assert graph.label_boolM["he11o"] == res.label_boolM["he11o"]
    assert res.transitive_closure_adjM().iseq(Matrix.sparse(BOOL, 3, 3).full(True))

    graph.scan("tests/graph1.txt")
    automaton.scan_regexp("tests/reg1.txt")
    res.intersection(graph, automaton)
    assert res.size == 10000

    graph.scan("tests/graph0.txt")
    automaton.scan_regexp("tests/reg1.txt")
    res.intersection(graph, automaton)
    assert not res.label_boolM


def test_mxm():
    A = Matrix.from_lists(
        [0, 0, 1, 3, 3, 4, 1, 5],
        [1, 3, 2, 4, 5, 2, 5, 4],
        [9, 3, 8, 6, 1, 4, 7, 2], )
    B = Matrix.from_lists(
        [0, 0, 1, 3, 3, 4, 1, 5],
        [2, 3, 3, 2, 5, 4, 5, 4],
        [9, 3, 8, 6, 2, 4, 5, 2], )
    C = A @ B
    assert C.iseq(Matrix.from_lists(
        [0, 0, 0, 1, 3, 5],
        [2, 3, 5, 4, 4, 4],
        [18, 72, 51, 14, 26, 8], ))


def test_enfa_inter():
    digits = [Symbol(x) for x in range(10)]
    states = [State("q" + str(x)) for x in range(3)]

    enfa1 = EpsilonNFA()
    enfa1.add_start_state(states[0])
    enfa1.add_final_state(states[2])
    for digit in digits:
        enfa1.add_transition(states[0], digit, states[1])
        enfa1.add_transition(states[1], digit, states[2])

    enfa2 = EpsilonNFA()
    enfa2.add_start_state(states[0])
    enfa2.add_final_state(states[2])
    for i in range(10):
        enfa2.add_transition(states[0], digits[i], states[1])
        if i & 1:
            enfa2.add_transition(states[1], digits[i], states[2])

    enfa = enfa1.get_intersection(enfa2)
    assert enfa.is_equivalent_to(enfa2)
