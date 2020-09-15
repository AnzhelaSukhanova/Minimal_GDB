from pyformlang.finite_automaton import EpsilonNFA, State, Symbol
from pygraphblas import *
import main


def test_graph_inter():
    graph = main.Graph()
    automaton = main.Graph()
    graph.scan("../tests/graph0.txt")
    automaton.scan_regexp("../tests/auto0.txt")
    automaton.intersection(graph)


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