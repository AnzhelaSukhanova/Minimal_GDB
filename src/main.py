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
        terminal_i = tools.indices_of_dup(list(map(grammar.body_term, cfg.productions)))
        terminal_i.pop(None)
        for label in graph.label_boolM:
            terminal = Terminal(label)
            if terminal in terminal_i:
                for k in range(len(terminal_i[terminal])):
                    var = list(cfg.productions)[terminal_i[terminal][k]].head
                    for i in range(graph.size):
                        for j in range(graph.size):
                            if (i, j) in graph.label_boolM[label]:
                                var_vertices.append([var, i, j])
        triple = var_vertices.copy()
        prod_var = grammar.pair_in_body(cfg.productions)
        while triple:
            var1, v1, v2 = triple.pop()
            for var2, u1, u2 in var_vertices:
                if u2 == v1:
                    for prod in prod_var:
                        if list(prod.body) == [var2, var1] and (prod.head, u1, v2) not in var_vertices:
                            triple.append((prod.head, u1, v2))
                            var_vertices.append((prod.head, u1, v2))
                elif u1 == v2:
                    for prod in prod_var:
                        if list(prod.body) == [var1, var2] and (prod.head, v1, u1) not in var_vertices:
                            triple.append((prod.head, v1, u1))
                            var_vertices.append((prod.head, v1, u1))
        reachability = Matrix.sparse(BOOL, graph.size, graph.size)
        for var, i, j in var_vertices:
            if var == cfg.start_symbol:
                reachability[i, j] = 1
        return reachability


def cfpq_MxM(graph, cfg):
    if graph.size == 0:
        return False
    else:
        res = Graph()
        res.size = graph.size
        res.label_boolM[cfg.start_symbol.value] = Matrix.sparse(BOOL, res.size, res.size)
        if cfg.generate_epsilon():
            res.label_boolM[cfg.start_symbol] = Matrix.identity(BOOL, graph.size)
        terminal_i = tools.indices_of_dup(list(map(grammar.body_term, cfg.productions)))
        terminal_i.pop(None)
        productions = []
        for label in graph.label_boolM:
            terminal = Terminal(label)
            if terminal in terminal_i:
                for k in range(len(terminal_i[terminal])):
                    var = list(cfg.productions)[terminal_i[terminal][k]].head
                    productions.append( list(cfg.productions)[terminal_i[terminal][k]])
                    if var in res.label_boolM:
                        res.label_boolM[var] += graph.label_boolM[label]
                    else:
                        res.label_boolM[var] = graph.label_boolM[label]
        productions = grammar.pair_in_body(productions)
        res_changes = True
        while res_changes:
            res_changes = False
            for prod in productions:
                last_nvals = res.label_boolM[prod.head].nvals
                with semiring.LOR_LAND_BOOL:
                    res.label_boolM[prod.head] += res.label_boolM[list(prod.body)[0]] @ \
                                                  res.label_boolM[list(prod.body)[1]]
                if res.label_boolM[prod.head].nvals != last_nvals:
                    res_changes = True
        return res.label_boolM[cfg.start_symbol]


def cfpq_tensor(graph, cfg):
    if graph.size == 0:
        return False
    else:
        res = graph.copy()
        res.label_boolM[cfg.start_symbol.value] = Matrix.sparse(BOOL, res.size, res.size)
        rec_auto = Graph()
        size = 0
        heads = {}
        for prod in cfg.productions:
            length = len(prod.body)
            if length > 0:
                size += length + 1
        rec_auto.size = size
        ver = 0
        for prod in cfg.productions:
            length = len(prod.body)
            if length > 0:
                rec_auto.start_states.append(ver)
                for i in range(length):
                    rec_auto.set(list(prod.body)[i].value, ver, ver + 1)
                    ver += 1
                rec_auto.final_states.append(ver)
                heads[ver - length, ver] = prod.head.value
                ver += 1
            else:
                S = cfg.start_symbol.value
                res.label_boolM[cfg.start_symbol.value] += Matrix.identity(BOOL, res.size)
        res_changes = True
        inter = Graph()
        tCl = inter.intersection(res, rec_auto).transitive_closure_squaring()
        n = inter.size
        while res_changes:
            last_nvals = tCl.nvals
            for i in range(n):
                for j in range(n):
                    if (i, j) in tCl:
                        s = i % rec_auto.size
                        f = j % rec_auto.size
                        if (s in rec_auto.start_states) and (f in rec_auto.final_states):
                            x = i // rec_auto.size
                            y = j // rec_auto.size
                            res.set(heads[s, f], x, y)
            tCl = inter.intersection(res, rec_auto).transitive_closure_squaring()
            if tCl.nvals == last_nvals:
                res_changes = False
        return res.label_boolM[cfg.start_symbol.value]


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
        print("'", word, "' —", grammar.cyk(cfg_in_cnf, word))
    elif args.type == ['graph-grammar']:
        graph = Graph()
        graph.scan(args.files[0])
        cfg = grammar.scan_cfg(args.files[1])
        res = cfpq_tensor(graph, cfg)
        if res is False:
            print(res)
        else:
            print(res.nvals)
        cfg_in_crf = grammar.to_crf(cfg)
        res = cfpq_hellings(graph, cfg_in_crf)
        if res is False:
            print(res)
        else:
            print(res.nvals)
        res = cfpq_MxM(graph, cfg_in_crf)
        if res is False:
            print(res)
        else:
            print(res.nvals)
    elif args.type == ['graph-regexp']:
        check_time.inter_time(args)
    elif args.type == ['graph'] or args.type == ['regexp']:
        check_time.clos_time(args)
    else:
        print("Unsupported request")
