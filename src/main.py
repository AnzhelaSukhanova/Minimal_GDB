import argparse
from pygraphblas import *
import check_time
from grammar import *


name_words = {'gr', 'connect', 's'}


def cfpq_hellings(graph, cfg):
    if graph.size == 0:
        return False
    var_vertices = list()
    if cfg.generate_epsilon():
        for i in range(graph.size):
            var_vertices.append([cfg.start_symbol, i, i])
    terminal_i = tools.indices_of_dup(list(map(body_term, cfg.productions)))
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
    prod_var = pair_in_body(cfg.productions)
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
    res = Graph()
    res.size = graph.size
    res.label_boolM[cfg.start_symbol] = Matrix.sparse(BOOL, res.size, res.size)
    if cfg.generate_epsilon():
        res.label_boolM[cfg.start_symbol] += Matrix.identity(BOOL, graph.size)
    terminal_i = tools.indices_of_dup(list(map(body_term, cfg.productions)))
    terminal_i.pop(None)
    for label in graph.label_boolM:
        terminal = Terminal(label)
        if terminal in terminal_i:
            for k in range(len(terminal_i[terminal])):
                var = list(cfg.productions)[terminal_i[terminal][k]].head
                if var in res.label_boolM:
                    res.label_boolM[var] += graph.label_boolM[label]
                else:
                    res.label_boolM[var] = graph.label_boolM[label]
    prod_var = pair_in_body(cfg.productions)
    res_changes = True
    while res_changes:
        res_changes = False
        for prod in prod_var:
            if (prod.head in res.label_boolM) and \
                    (list(prod.body)[0] in res.label_boolM) and \
                    (list(prod.body)[1] in res.label_boolM):
                last_nvals = res.label_boolM[prod.head].nvals
                with semiring.LOR_LAND_BOOL:
                    res.label_boolM[prod.head] += res.label_boolM[list(prod.body)[0]] @ \
                                                  res.label_boolM[list(prod.body)[1]]
                if res.label_boolM[prod.head].nvals != last_nvals:
                    res_changes = True
    return res.label_boolM[cfg.start_symbol]


def cfpq_tensor(graph, cfg, rec_auto, heads):
    if graph.size == 0:
        return False
    res = graph.copy()
    res.label_boolM[cfg.start_symbol.value] = Matrix.sparse(BOOL, res.size, res.size)
    if cfg.generate_epsilon():
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


def syn_analyzer(syntax, prog):
    f = open(prog, 'r')
    is_correct = 1
    for line in f:
        line = line.rstrip()
        while line.endswith(('\\')):
            line = line[:len(line) - 1] + " " + f.readline()
            line = line.rstrip()
        words = line.split()
        old_line = line
        i = 0
        prod_len = len(words)
        while i < prod_len:
            if words[i] in name_words:
                if len(words) == i + 1:
                    print("\nIncorrect syntax")
                    print("Name/symbol is missing in '" + old_line + "'")
                    is_correct = 0
                else:
                    word_len = len(words[i + 1])
                    words = words[:i + 1] + list(words[i + 1]) + words[i + 2:]
                    i += word_len
                    prod_len += word_len - 1
                    line = " ".join(words)
            i += 1
        if is_correct and not cyk(syntax, line):
            print("\nIncorrect syntax")
            print("Problem in '" + old_line + "'")
            is_correct = 0
    f.close()
    if is_correct:
        print("\nCorrect syntax")
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', nargs=1,
        choices=['clos_graph', 'clos_regexp', 'inter', 'sa', 'cfpq'])
    parser.add_argument(
        'files', nargs='+')
    args = parser.parse_args()
    if args.type == ['sa']:
        cfg = scan_cfg(args.files[0])
        cfg.variables.add(Variable("Name"))
        add_letter_prod(cfg, Variable('Name'))
        add_digit_prod(cfg, Variable('Name'))
        cfg_in_cnf = to_cnf(cfg)
        prog = args.files[1]
        syn_analyzer(cfg_in_cnf, prog)
    elif args.type == ['cfpq']:
        graph = Graph()
        graph.scan(args.files[0])
        cfg = scan_cfg(args.files[1])
        rec_auto, heads = build_rec_automaton(cfg)
        res = cfpq_tensor(graph, cfg, rec_auto, heads)
        if res is False:
            print(res)
        else:
            print(res.nvals)
        cfg_in_cnf = to_cnf(cfg)
        res = cfpq_hellings(graph, cfg_in_cnf)
        if res is False:
            print(res)
        else:
            print(res.nvals)
        res = cfpq_MxM(graph, cfg_in_cnf)
        if res is False:
            print(res)
        else:
            print(res.nvals)
    elif args.type == ['inter']:
        check_time.inter_time(args)
    elif args.type == ['clos_graph'] or args.type == ['clos_regexp']:
        check_time.clos_time(args)
    else:
        print("Unsupported request")
