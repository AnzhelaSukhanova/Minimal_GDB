from pyformlang.regular_expression import Regex
from pygraphblas import *
import timeit
import argparse
from statistics import fmean, variance


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
            self.size = max(max(int(i), int(j)) + 1, self.size)
        f.close()
        f = open(file_name, 'r')
        for line in f:
            i, w, j = line.split(" ")
            i = int(i)
            j = int(j)
            if w in self.label_boolM:
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

    def intersection(self, fst, snd):
        self.__init__()
        for label in fst.label_boolM:
            if label in snd.label_boolM:
                self.label_boolM[label] = \
                    fst.label_boolM[label].kronecker(snd.label_boolM[label])
        self.size = fst.size * snd.size
        for i in fst.start_states:
            for j in snd.start_states:
                self.start_states.append(i * fst.size + j)
        for i in fst.final_states:
            for j in snd.final_states:
                self.final_states.append(i * fst.size + j)
        return self

    def transitive_closure_adjM(self):
        res = Matrix.identity(BOOL, self.size)
        for label in self.label_boolM:
            res = res + self.label_boolM[label]
        for i in range(self.size):
            last_nvals = res.nvals
            with semiring.LOR_LAND_BOOL:
                res += res @ res
            if res.nvals == last_nvals:
                break
        return res

    def transitive_closure_squaring(self):
        res = Matrix.identity(BOOL, self.size)
        for label in self.label_boolM:
            res = res + self.label_boolM[label]
        for i in range(self.size):
            old_nvals = res.nvals
            with semiring.LOR_LAND_BOOL:
                res = res @ res
            if res.nvals == old_nvals:
                break
        return res

    def reachability_from(self, set):
        res = self.transitive_closure_adjM()
        for i in range(self.size):
            if i not in set:
                res.assign_row(i, Vector.sparse(BOOL, self.size).full(0))
        return res

    def reachability_from_to(self, set_from, set_to):
        res = self.transitive_closure_adjM()
        for i in range(self.size):
            if i not in set_from:
                res.assign_row(i, Vector.sparse(BOOL, self.size).full(0))
            if i not in set_to:
                res.assign_col(i, Vector.sparse(BOOL, self.size).full(0))
        return res

    def print_inter(self):
        for label in self.label_boolM:
            print(label, "—", self.label_boolM[label].nvals)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--type', nargs=1,
        choices=['graph', 'regexp'], required=False)
    parser.add_argument(
        'files', nargs='+')
    args = parser.parse_args()

    graph = Graph()
    if len(args.files) == 2:
        automaton = Graph()
        res = Graph()
        graph.scan(args.files[0])
        automaton.scan_regexp(args.files[1])
        time_inter = timeit.repeat("res.intersection(automaton, graph)",
                                   setup="from __main__ import Graph, res, graph, automaton",
                                   repeat=5,
                                   number=1)
        res.intersection(automaton, graph)
        f = open("time_out.txt", 'a')
        f.write(str(args.files[0]) + " " + str(args.files[1]) + "\n")
        average = round(fmean(time_inter), 6)
        D = round(variance(time_inter), 6)
        time_inter = [round(t, 6) for t in time_inter]
        f.write("intersection: " + str(time_inter) + " " +
                str(average) + " " +
                str(D) + "\n")

        time_print = timeit.repeat("res.print_inter()",
                                   setup="from __main__ import Graph, res",
                                   repeat=5,
                                   number=1)
        average = round(fmean(time_print), 6)
        D = round(variance(time_print), 6)
        time_print = [round(t, 6) for t in time_print]
        f.write("time_print: " + str(time_print) + " " +
                str(average) + " " +
                str(D) + "\n\n")
        f.close()

    elif len(args.files) == 1:
        if args.type[0] == "graph":
            graph.scan(args.files[0])
        elif args.type[0] == "regexp":
            graph.scan_regexp(args.files[0])
        res = Matrix.identity(BOOL, graph.size)
        f = open("time_out.txt", 'a')
        f.write(str(args.files[0]) + "\n")
        time_clos_adjM = timeit.repeat("res = graph.transitive_closure_adjM()",
                                       setup="from __main__ import Graph, graph, res",
                                       repeat=5,
                                       number=1)
        res = graph.transitive_closure_adjM()
        average = round(fmean(time_clos_adjM), 6)
        D = round(variance(time_clos_adjM), 6)
        time_clos_adjM = [round(t, 6) for t in time_clos_adjM]
        f.write("transitive_closure_adjM: " + str(time_clos_adjM) + " " +
                str(average) + " " +
                str(D) + " " +
                str(res.nvals) + "\n")

        time_clos_squar = timeit.repeat("res = graph.transitive_closure_squaring()",
                                        setup="from __main__ import Graph, graph, res",
                                        repeat=5,
                                        number=1)
        res = graph.transitive_closure_squaring()
        average = round(fmean(time_clos_squar), 6)
        D = round(variance(time_clos_squar), 6)
        time_clos_squar = [round(t, 6) for t in time_clos_squar]
        f.write("transitive_closure_squaring: " + str(time_clos_squar) + " " +
                str(average) + " " +
                str(D) + " " +
                str(res.nvals) + "\n\n")
        f.close()
