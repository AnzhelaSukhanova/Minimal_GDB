from pyformlang.cfg import CFG, Epsilon, Production, Variable, Terminal
from classes import Graph
import tools


def pair_in_body(productions):
    res = []
    for prod in productions:
        if len(prod.body) == 2:
            res.append(prod)
    return res


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
    return cfg.to_normal_form()


def to_crf(cfg):
    return cfg.to_normal_form()


def body_term(production):
    if production.body:
        if len(production.body) == 1:
            return list(production.body)[0]
    else:
        return Epsilon()


def cyk(cfg, word):
    word = word.split()
    word_size = len(word)
    if word_size == 0:
        return cfg.generate_epsilon()
    var_n = len(cfg.variables)
    matrix = [[[0 for _ in range(word_size)] for _ in range(word_size)] for _ in range(var_n)]
    var_i = dict(zip(cfg.variables, range(var_n)))
    sym_i = tools.indices_of_dup(word)
    terminal_i = tools.indices_of_dup(list(map(body_term, cfg.productions)))
    for sym in word:
        terminal = Terminal(sym) if sym != ' ' else Epsilon()
        if terminal in terminal_i:
            for i in sym_i[sym]:
                for j in terminal_i[terminal]:
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
    return bool(matrix[var_i[cfg.start_symbol]][0][word_size - 1])


def build_rec_automaton(cfg):
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
    return rec_auto, heads
