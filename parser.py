import lexis
import syntax
import semantics


def analyze(data):
    analyzer = syntax.analyzer
    try:
        result = analyzer.parse(data)
    except syntax.SyntaxError as e:
        print e.message
        result = None
    return result


def interpret(data):
    root_node = analyze(data)
    if root_node is not None:
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
