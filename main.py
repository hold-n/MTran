#! /bin/python

import sys
from collections import defaultdict

import parser


def print_token_stat(data):
    stat = defaultdict(list)
    for token in parser.tokenize(data):
        stat[token.type].append((token.value, token.lineno))
    _print_stat(stat)


def print_token_list(data):
    for token in parser.tokenize(data):
        lineno = str(token.lineno).ljust(4)
        if token.type.isalpha():  # empiric rule
            print "line {} - {}: '{}'".format(
                lineno, token.type, token.value
            )
        else:
            print "line {} - {}".format(lineno, token.type)


def print_tree(data):
    root = parser.analyze(data)
    _print_tree(root)


def main():
    with open('sample.ts') as f:
        data = f.read()
    # print_token_stat(data)
    # print_token_list(data)
    # print_tree(data)
    parser.interpret(data)


def _print_tree(node, indent=0):
    pad = '  ' * indent
    print pad, node
    next_indent = indent + 1
    for child in node.iterchildren():
        _print_tree(child, next_indent)


def _print_stat(stat):
    for key in stat:
        print key
        for value, lineno in stat[key]:
            print '\t{} - line #{}'.format(value, lineno)


if __name__ == '__main__':
    main()
