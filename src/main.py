import argparse
import check_time
from cfpq import *
from pyformlang.regular_expression import *

name_words = {'gr', 'connect', 's'}


def nullable(regexp):
    if '(' in regexp:
        brackets = list()
        i = 0
        for sym in regexp:
            if sym == '(':
                brackets.append(i)
            if sym == ')':
                old_len = len(regexp)
                sim_part = regexp[brackets[len(brackets) - 1] + 1:i]
                regexp = regexp[:brackets[len(brackets) - 1]] + str(simple_nullable(sim_part)) + regexp[i + 1:]
                i -= old_len - len(regexp)
                brackets = brackets[:len(brackets) - 1]
            i += 1
    return simple_nullable(regexp)


def simple_nullable(regexp):
    if regexp == '$':
        return True
    elif regexp == 'True' or regexp == 'False':
        return regexp
    elif '|' in regexp:
        parts = regexp.split('|', 1)
        return simple_nullable(parts[0]) or simple_nullable(parts[1])
    elif '.' in regexp:
        parts = regexp.split('.', 1)
        return simple_nullable(parts[0]) and simple_nullable(parts[1])
    elif '*' in regexp:
        return True
    else:
        return False


def derivative(sym, tree):
    if tree.head.value == 'Empty':
        return ''
    elif tree.head.value == 'Union':
        der0 = derivative(sym, tree.sons[0])
        der1 = derivative(sym, tree.sons[1])
        if der0 == '' and der1 == '':
            return ''
        elif der0 == '':
            return der1
        elif der1 == '':
            return der0
        else:
            return der0 + '|' + der1
    elif tree.head.value == 'Concatenation':
        der0 = derivative(sym, tree.sons[0])
        if simple_nullable(str(tree.sons[0])):
            der1 = derivative(sym, tree.sons[1])
            if der0 == '' and der1 == '':
                return ''
            elif der0 == '':
                return der1
            elif der1 == '':
                return der0 + '.' + str(tree.sons[1])
            else:
                return der0 + '.' + str(tree.sons[1]) + '|' + der1
        else:
            if der0 == '':
                return ''
            else:
                return der0 + '.' + str(tree.sons[1])
    elif tree.head.value == 'Kleene Star':
        der = derivative(sym, tree.sons[0])
        if der == '':
            return ''
        else:
            return der + '.' + str(tree)
    else:
        if tree.head.value == sym:
            return '$'
        else:
            return ''


def derivative_check(word, regexp):
    if word == '':
        return False
    alphabet = [el for el in regexp.replace('(', '*').replace(')', '*').replace('|', '*').replace('.', '*').split('*')
                if el != '' and el != '$']
    i = 0
    count = 0
    sym = ''
    while i < len(word):
        sym += word[i]
        if sym in alphabet:
            tree = Regex(regexp)
            regexp = derivative(sym, tree)
            count += len(sym)
            sym = ''
        i += 1
    if count < len(word) and word != '$':
        return False
    return nullable(regexp)


def syn_analyzer(syntax, prog):
    f = open(prog, 'r')
    is_correct = 1
    for line in f:
        need_cyk = 1
        line = line.rstrip()
        while line.endswith(('\\')):
            line = line[:len(line) - 1] + ' ' + f.readline()
            line = line.rstrip()
        words = line.split()
        old_line = line
        i = 0
        prod_len = len(words)
        while i < prod_len:
            if words[i] in name_words:
                if len(words) == i + 1:
                    print('Name/symbol is missing in '' + old_line + ''')
                    is_correct = 0
                    need_cyk = 0
                else:
                    word_len = len(words[i + 1])
                    words = words[:i + 1] + list(words[i + 1]) + words[i + 2:]
                    i += word_len
                    prod_len += word_len - 1
                    line = ' '.join(words)
            i += 1
        if need_cyk and not cyk(syntax, line):
            print('Problem in '' + old_line + ''')
            is_correct = 0
    f.close()
    if is_correct:
        print('\nCorrect syntax')
        return True
    else:
        print('\nIncorrect syntax')
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'type', nargs=1,
        choices=['clos_graph', 'clos_regexp', 'inter', 'sa', 'cfpq', 'der'])
    parser.add_argument(
        'files', nargs='+')
    args = parser.parse_args()

    if args.type == ['der']:
        f = open(args.files[0], 'r')
        regexp = f.read().rstrip('\n')
        f.close()
        word = input()
        print(derivative_check(word, regexp))

    elif args.type == ['sa']:
        cfg = scan_cfg(args.files[0])
        cfg.variables.add(Variable('Name'))
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
        print('Unsupported request')
