import argparse
from pyformlang.cfg import CFG, Epsilon, Production, Variable, Terminal
from pygraphblas import *
import check_time
import tools
from classes import Graph


def scan_cfg(file_name):
    f = open(file_name, 'r')
    productions = []
    for line in f:
        read_prod = line.split()
        productions.append(read_prod[0] + " -> " + " ".join(read_prod[1:]))
    f.close()
    cfg = CFG.from_text("\n".join(productions))
    return cfg


def to_cnf(cfg):
    if cfg.generate_epsilon():
        cfg = cfg.to_normal_form()
        new_start_symbol = Variable(cfg.start_symbol.value + "'")
        cfg.productions.add(Production(new_start_symbol, []))
        res = CFG(variables=cfg.variables,
                  terminals=cfg.terminals,
                  start_symbol=new_start_symbol)
        res.variables.add(new_start_symbol)
        for production in cfg.productions:
            if production.head == cfg.start_symbol:
                res.productions.add(Production(new_start_symbol, production.body))
            res.productions.add(production)
        return res
    else:
        return cfg.to_normal_form()


def to_crf(cfg):
    return cfg.to_normal_form()


def body_fst(production):
    if production.body:
        return list(production.body)[0]
    else:
        return Epsilon()


def cyk(cfg, word):
    word = word.split()
    word_size = len(word)
    if word_size == 0:
        print("' ' —", cfg.generate_epsilon())
        return cfg.generate_epsilon()
    else:
        var_n = len(cfg.variables)
        matrix = [[[0 for _ in range(word_size)] for _ in range(word_size)] for _ in range(var_n)]
        var_i = dict(zip(cfg.variables, range(var_n)))
        sym_i = tools.indices_of_dup(word)
        body_i = tools.indices_of_dup(list(map(body_fst, cfg.productions)))
        for sym in word:
            terminal = Terminal(sym) if sym != ' ' else Epsilon()
            if terminal in body_i:
                for i in sym_i[sym]:
                    for j in body_i[terminal]:
                        matrix[var_i[list(cfg.productions)[j].head]][i][i] = 1
        for m in range(1, word_size):
            for i in range(word_size - m):
                j = i + m
                for var in range(var_n):
                    for production in cfg.productions:
                        for k in range(i, j):
                            if production.head == tools.get_key(var_i, var) and \
                                    len(production.body) == 2:
                                matrix[var][i][j] += matrix[var_i[list(production.body)[0]]][i][k] * \
                                                     matrix[var_i[list(production.body)[1]]][k + 1][j]
                                if matrix[var][i][j]:
                                    break
                        if matrix[var][i][j]:
                            break
    print("'", " ".join(word), "' —", bool(matrix[var_i[cfg.start_symbol]][0][word_size - 1]))
    return bool(matrix[var_i[cfg.start_symbol]][0][word_size - 1])


def hellings_algo(graph, cfg):
    if graph.size == 0:
        return cfg.generate_epsilon()
    else:
        var_vertices = list()
        body_i = tools.indices_of_dup(list(map(body_fst, cfg.productions)))
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
        cfg = scan_cfg(args.files[0])
        cfg_in_cnf = to_cnf(cfg)
        print("Enter the word you want to check:")
        word = input()
        cyk(cfg_in_cnf, word)
    elif args.type == ['graph-grammar']:
        graph = Graph()
        graph.scan(args.files[0])
        cfg = scan_cfg(args.files[1])
        cfg_in_crf = to_crf(cfg)
        print(hellings_algo(graph, cfg_in_crf).select("==", 1).nvals)
    elif args.type == ['graph-regexp']:
        check_time.inter_time(args)
    elif args.type == ['graph'] or args.type == ['regexp']:
        check_time.clos_time(args)
    else:
        print("Unsupported request")
