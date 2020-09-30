from pyformlang.finite_automaton import EpsilonNFA, State, Symbol
from pygraphblas import *
from classes import Graph
import main


def test_cyk():
    cfg = main.scan_cfg("tests/grammar0.txt")
    cfg_in_cnf = main.to_cnf(cfg)
    print("\ngrammar0.txt:")
    assert main.cyk(cfg_in_cnf, "5 5 5 5 5 5")
    assert not main.cyk(cfg_in_cnf, "1 2 3 4 5")
    assert main.cyk(cfg_in_cnf, "4 4 5")
    assert not main.cyk(cfg_in_cnf, "55")
    assert main.cyk(cfg_in_cnf, " ")

    cfg = main.scan_cfg("tests/grammar1.txt")
    cfg_in_cnf = main.to_cnf(cfg)
    print("\ngrammar1.txt:")
    assert main.cyk(cfg_in_cnf, "5 5 5 5 5 5")
    assert not main.cyk(cfg_in_cnf, "1 2 3 4 5")
    assert not main.cyk(cfg_in_cnf, "4 4 5")
    assert not main.cyk(cfg_in_cnf, "55")
    assert not main.cyk(cfg_in_cnf, " ")


def test_hellings():
    graph = Graph()
    graph.scan("tests/graph2.txt")
    cfg = main.scan_cfg("tests/grammar0.txt")
    cfg_in_crf = main.to_crf(cfg)
    cfg_in_cnf = main.to_cnf(cfg)
    print("\ngraph2.txt", "grammar0.txt:")
    res = main.hellings_algo(graph, cfg_in_crf)
    print("CRF:\n", res)
    assert res.select("==", 1).nvals == 4
    res = main.hellings_algo(graph, cfg_in_cnf)
    print("CNF:\n", res)
    assert res.select("==", 1).nvals == 6

    graph.scan("tests/graph_empty.txt")
    assert not main.hellings_algo(graph, cfg_in_crf)

    graph.scan("tests/graph_loop.txt")
    assert main.hellings_algo(graph, cfg_in_crf).select("==", 1).nvals == 1

    graph.scan("tests/graph0.txt")
    assert main.hellings_algo(graph, cfg_in_crf).select("==", 1).nvals == 0


def test_graph_inter():
    graph = Graph()
    automaton = Graph()
    res = Graph()

    print("\n\ngraph0.txt", "reg0.txt:")
    graph.scan("tests/graph0.txt")
    automaton.scan_regexp("tests/reg0.txt")
    res.intersection(graph, automaton)
    assert graph.label_boolM["he11o"] == res.label_boolM["he11o"]
    assert res.transitive_closure_adjM() == Matrix.dense(INT8, 3, 3).full(1)
    res.print_inter()
    print()

    print("graph1.txt", "reg1.txt:")
    graph.scan("tests/graph1.txt")
    automaton.scan_regexp("tests/reg1.txt")
    res.intersection(graph, automaton)
    assert res.size == 10000
    res.print_inter()
    print()

    graph.scan("tests/graph0.txt")
    automaton.scan_regexp("tests/reg1.txt")
    res.intersection(graph, automaton)
    assert not res.label_boolM
    res.print_inter()
    print()


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
