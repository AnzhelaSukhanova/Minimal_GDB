import argparse
from pyformlang.cfg import CFG, Epsilon, Production, Variable, Terminal
import check_time
from collections import defaultdict


def scan_grammar(file_name):
    f = open(file_name, 'r')
    productions = []
    for line in f:
        read_prod = line.split()
        productions.append(read_prod[0] + " -> " + " ".join(read_prod[1:]))
    f.close()
    cfg = CFG.from_text("\n".join(productions))
    return cfg


def to_cfn(grammar):
    cfg = grammar
    if cfg.generate_epsilon():
        cfg = cfg.to_normal_form()
        new_start_symbol = Variable(cfg.start_symbol.value + "'")
        cfg.productions.add(Production(new_start_symbol, []))
        for production in cfg.productions:
            if production.head == cfg.start_symbol:
                cfg.productions.add(Production(new_start_symbol, production.body))
                cfg.productions.remove(production)
        cfg.variables.add(new_start_symbol)
        res = CFG(variables=cfg.variables,
                  terminals=cfg.terminals,
                  productions=cfg.productions,
                  start_symbol=new_start_symbol)
    else:
        res = cfg.to_normal_form()
    return res


def to_crf(cfg):
    return cfg.to_normal_form()


def indices_of_dup(word):
    d = defaultdict(list)
    for index, sym in enumerate(word):
        d[sym].append(index)
    return d


def body_fst(production):
    if production.body:
        return production.body.pop()
    else:
        return Epsilon()


def cyk(cfg, word):
    word = word.split()
    word_size = len(word)
    if word_size == 0:
        return cfg.generate_epsilon()
    else:
        var_n = len(cfg.variables)
        matrix = [[[False for _ in range(word_size)] for _ in range(word_size)] for _ in range(var_n)]
        var_i = dict(zip(cfg.variables, range(var_n)))
        sym_i = indices_of_dup(word)
        body_i = indices_of_dup(list(map(body_fst, cfg.productions)))
        for sym in word:
            terminal = Terminal(sym) if sym != ' ' else Epsilon()
            if terminal in body_i:
                for i in sym_i[sym]:
                    for j in body_i[terminal]:
                        matrix[var_i[list(cfg.productions)[j].head]][i][i] = True
        for i in range(word_size):
            for j in range(word_size):
                for var in range(var_n):
                    for k in range(j):
                        for production in cfg.productions:
                            if production.head == Variable(list(cfg.productions)[var].head) and \
                                    len(production.body) == 2:
                                matrix[var][i][j] += matrix[var_i[list(production.body)[0]]][i][k] * \
                                                     matrix[var_i[list(production.body)[1]]][k][j]
                            if matrix[var][i][j]:
                                break
                        if matrix[var][i][j]:
                            break
                    if matrix[var][i][j]:
                        break
    '''for k in range(var_n):
        for i in range(word_size):
            for j in range(word_size):
                print(list(cfg.variables)[k], i, j, matrix[k][i][j])
    print()'''
    return matrix[var_i[cfg.start_symbol]][0][0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--type', nargs=1,
        choices=['graph', 'regexp', 'grammar'], required=False)
    parser.add_argument(
        'files', nargs='+')
    args = parser.parse_args()
    if args.type == ['grammar']:
        cfg = scan_grammar(args.files[0])
        cfg_in_cfn = to_cfn(cfg)
        word = input()
        print("'", word, "' —", cyk(cfg_in_cfn, word))
    else:
        if len(args.files) == 2:
            check_time.inter_time(args)
        elif len(args.files) == 1 and (args.type == ['graph'] or args.type == ['regexp']):
            check_time.clos_time(args)
        else:
            print("Unsupported request")
