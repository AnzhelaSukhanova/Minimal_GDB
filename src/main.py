from pyformlang.regular_expression import Regex
from pygraphblas import *
import sys


class Graph:
    def __init__(self):
        self.label_boolM = {}
        self.size = 0
        self.start_states = []
        self.final_states = []

    def scan(self, file_name):
        self.__init__()
        f = open(file_name, 'r')
        for line in f:
            i, w, j = line.split(" ")
            i = int(i)
            j = int(j)
            self.size = max(max(i, j) + 1, self.size)
            if w in self.label_boolM:
                if self.size > self.label_boolM[w].nrows:
                    self.label_boolM[w].resize(self.size, self.size)
                self.label_boolM[w][i, j] = 1
            else:
                bool_M = Matrix.sparse(BOOL, self.size, self.size)
                bool_M[i, j] = 1
                self.label_boolM[w] = bool_M
        f.close()
        for i in range(self.size):
            self.start_states.append(i)
            self.final_states.append(i)
        return self

    def scan_regexp(self, file_name):
        self.__init__()
        f = open(file_name, 'r')
        automaton = Regex(f.read().rstrip()).to_epsilon_nfa()\
            .to_deterministic().minimize()
        f.close()
        states = {}
        i = 0
        for state in automaton._states:
            if state not in states:
                states[state] = i
                i = i + 1
        self.size = i
        for i in automaton._states:
            for symbol in automaton._input_symbols:
                in_states = automaton._transition_function(i, symbol)
                for j in in_states:
                    if symbol in self.label_boolM:
                        self.label_boolM[symbol][states[i], states[j]] = 1
                    else:
                        bool_M = Matrix.sparse(BOOL, self.size, self.size)
                        bool_M[states[i], states[j]] = 1
                        self.label_boolM[symbol] = bool_M
        self.start_states.append(states[automaton.start_state])
        for state in automaton._final_states:
            self.final_states.append(states[state])
        return self

    def intersection(self, other):
        res = Graph()
        for label in self.label_boolM:
            if label in other.label_boolM:
                res.label_boolM[label] = \
                    self.label_boolM[label].kronecker(other.label_boolM[label])
        res.size = self.size * other.size
        for i in self.start_states:
            for j in other.start_states:
                res.start_states.append(i * self.size + j)
        for i in self.final_states:
            for j in other.final_states:
                res.final_states.append(i * self.size + j)
        for label in res.label_boolM:
            print(label, "—", res.label_boolM[label].nvals)
        print()
        return res

    def reachability_all(self):
        res = Matrix.random(BOOL, self.size, self.size, 0).full(0)
        for label in self.label_boolM:
            if self.label_boolM[label].nrows < self.size:
                self.label_boolM[label].resize(self.size, self.size)
            res = res | self.label_boolM[label]
        for i in range(self.size):
            res += res @ res
        return res

    def reachability_from(self, set):
        res = self.reachability_all()
        for i in range(self.size):
            if i not in set:
                res.assign_row(i, Vector.sparse(BOOL, self.size).full(0))
        return res

    def reachability_from_to(self, set_from, set_to):
        res = self.reachability_all()
        for i in range(self.size):
            if i not in set_from:
                res.assign_row(i, Vector.sparse(BOOL, self.size).full(0))
            if i not in set_to:
                res.assign_col(i, Vector.sparse(BOOL, self.size).full(0))
        return res


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("You didn't provide a file with an input graph/automaton")
    else:
        graph = Graph()
        automaton = Graph()
        graph.scan(sys.argv[1])
        automaton.scan_regexp(sys.argv[2])
        automaton.intersection(graph)
