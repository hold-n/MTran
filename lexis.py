from ply import lex
from ply.lex import TOKEN


ident = r'(?<!\d)[$_a-zA-Z][$_a-zA-Z0-9]*'
number = r'(?<![a-zA-Z])\d+(\.\d+)?'
string = r"\'[^\']*\'"  # NOTE: only single quotes supported for now

reserved = {
    'any': 'ANY_TYPE',
    'boolean': 'BOOLEAN_TYPE',
    'class': 'CLASS',
    'constructor': 'CONSTRUCTOR',
    'else': 'ELSE',
    'false': 'FALSE',
    'function': 'FUNCTION',
    'if': 'IF',
    'let': 'LET',
    'new': 'NEW',
    'null': 'NULL',
    'number': 'NUMBER_TYPE',
    'return': 'RETURN',
    'string': 'STRING_TYPE',
    'this': 'THIS',
    'true': 'TRUE',
    'undefined': 'UNDEFINED',
    'while': 'WHILE',
}

tokens = [
    'AND',
    'COMMENT',
    'CONSOLE_LOG',  # a workaround for now
    'ID',
    'LESS_OR_EQUAL',
    'MORE_OR_EQUAL',
    'NUMBER',
    'OR',
    'STRICT_EQUALS',
    'STRICT_NOT_EQUAL',
    'STRING',
] + reserved.values()

literals = [
    '!',
    '(',
    ')',
    '*',
    '+',
    ',',
    '-',
    '.',
    '/',
    ':',
    ';',
    '<',
    '=',
    '>',
    '[',
    ']',
    '{',
    '}',
]

@TOKEN(r'console\.log')
def t_CONSOLE_LOG(t):  # a function so that it would take precedence
    return t

@TOKEN(r'\/\/[^\n]*\n')
def t_COMMENT(t):
    t.lexer.lineno += 1

@TOKEN('NaN')
def t_NAN(t):
    t.type = 'NUMBER'
    t.value = float('nan')
    return t

@TOKEN('Infinity')
def t_INFINITY(t):
    t.type = 'NUMBER'
    t.value = float('inf')
    return t

@TOKEN(ident)
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')
    return t

@TOKEN(number)
def t_NUMBER(t):
    t.value = float(t.value)
    return t

@TOKEN(string)
def t_STRING(t):
    t.value = t.value[1:-1]
    return t

@TOKEN(r'\n+')
def t_newline(t):
    t.lexer.lineno += len(t.value)

t_AND = r'\&{2}'
t_OR = r'\|{2}'
t_STRICT_EQUALS = r'\={3}'
t_STRICT_NOT_EQUAL = 'r\!\={2}'
t_LESS_OR_EQUAL = r'\<\='
t_MORE_OR_EQUAL = r'\>\='


t_ignore = " \t"

def t_error(t):
    # TODO: skip while not space or reserved or smth
    print("Lexical error: unidentified token '{}' on line #{}".format(
        t.value[0], t.lexer.lineno
    ))
    t.lexer.skip(1)

lexer = lex.lex()
