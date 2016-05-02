import lexis
import syntax
import semantics


def analyze(data):
    analyzer = syntax.analyzer
    return analyzer.parse(data)


def interpret(data):
    root_node = analyze(data)
    try:
        root_node.run()
    except semantics.SemanticError as e:
        print e.message


def tokenize(data):
    lexer = lexis.lexer
    lexer.input(data)
    while True:
        token = lexer.token()
        if token is None:
            raise StopIteration()
        yield token
