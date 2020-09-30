from collections import defaultdict


def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key
    print("Key doesn't exist")


def indices_of_dup(word):
    d = defaultdict(list)
    for index, sym in enumerate(word):
        d[sym].append(index)
    return d
