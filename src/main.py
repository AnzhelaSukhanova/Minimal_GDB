import argparse
from pyformlang.cfg import Terminal
from pygraphblas import *
from classes import Graph
import check_time
import tools
import grammar


def cfpq_hellings(graph, cfg):
    if graph.size == 0:
        return False
    else:
        var_vertices = list()
        if cfg.generate_epsilon():
            for i in range(graph.size):
                var_vertices.append([cfg.start_symbol, i, i])
        body_i = tools.indices_of_dup(list(map(grammar.body_fst, cfg.productions)))
        for label in graph.label_boolM:
            terminal = Terminal(label)
            if terminal in body_i:
                for k in range(len(body_i[terminal])):
                    var = list(cfg.productions)[body_i[terminal][k]].head
                    for i in range(graph.size):
                        for j in range(graph.size):
                            if graph.label_boolM[label][i, j]:
                                var_vertices.append([var, i, j])
        triple = var_vertices.copy()
        while triple:
            var1, v1, v2 = triple.pop()
            for var2, u1, u2 in var_vertices:
                if u2 == v1:
                    for production in cfg.productions:
                        if list(production.body) == {var2, var1} and (production.head, u1, v2) not in var_vertices:
                            triple.append((production.head, u1, v2))
                            var_vertices.append((production.head, u1, v2))
                elif u1 == v2:
                    for production in cfg.productions:
                        if list(production.body) == {var1, var2} and (production.head, v1, u1) not in var_vertices:
                            triple.append((production.head, v1, u1))
                            var_vertices.append((production.head, v1, u1))
        reachability = Matrix.sparse(BOOL, graph.size, graph.size).full(0)
        for var, i, j in var_vertices:
            if var == cfg.start_symbol:
                reachability[i, j] = 1
        return reachability


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', nargs=1,
        choices=['graph', 'regexp', 'grammar', 'graph-grammar', 'graph-regexp'])
    parser.add_argument(
        'files', nargs='+')
    args = parser.parse_args()
    if args.type == ['grammar']:
        cfg = grammar.scan_cfg(args.files[0])
        cfg_in_cnf = grammar.to_cnf(cfg)
        print("Enter the word you want to check:")
        word = input()
        grammar.cyk(cfg_in_cnf, word)
    elif args.type == ['graph-grammar']:
        graph = Graph()
        graph.scan(args.files[0])
        cfg = grammar.scan_cfg(args.files[1])
        cfg_in_crf = grammar.to_crf(cfg)
        res = cfpq_hellings(graph, cfg_in_crf)
        if res is False:
            print(res)
        else:
            print(res.select("==", 1).nvals)
    elif args.type == ['graph-regexp']:
        check_time.inter_time(args)
    elif args.type == ['graph'] or args.type == ['regexp']:
        check_time.clos_time(args)
    else:
        print("Unsupported request")
