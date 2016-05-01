from ply import yacc

import lexis
from lexis import tokens, literals
from semantics import *


precedence = (
    ('right', '='),
    ('left', '(', ')'),
    ('nonassoc', '<', '>', 'LESS_OR_EQUAL', 'MORE_OR_EQUAL', 'STRICT_EQUALS', 'STRICT_NOT_EQUAL'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('nonassoc', '!'),
    ('nonassoc', 'UMINUS'),
    ('left', '.'),
)


# TODO: reorder rules in sensible order
# TODO: add support for arrays
# TODO: add support for object literals
# TODO: allow implicit 'any' => remove rule and token for constructor
# TODO: support for 'for' loop

def p_root(p):
    "root : language_item_list"
    p[0] = ScopeNode(p[1])

def p_language_item_list_empty(p):
    "language_item_list : empty"
    p[0] = []

def p_language_item_list(p):
    "language_item_list : language_item_list language_item"
    p[1].append(p[2])
    p[0] = p[1]

def p_language_item_block(p):
    "language_item_block : '{' language_item_list '}'"
    p[0] = ScopeNode(p[2])

def p_language_item(p):
    '''language_item : function_decl
                        | class
                        | procedural_item'''
    p[0] = p[1]

def p_procedural_item(p):
    '''procedural_item : if
                        | loop
                        | statement ';' '''
    p[0] = p[1]

def p_procedural_item_list_empty(p):
    "procedural_item_list : empty"
    p[0] = []

def p_procedural_item_list(p):
    '''procedural_item_list : procedural_item_list procedural_item'''
    p[1].append(p[2])
    p[0] = p[1]

def p_procedural_item_block(p):
    "procedural_item_block : '{' procedural_item_list '}'"
    p[0] = ScopeNode(p[2])

def p_statement_return(p):
    "statement : RETURN expression"
    p[0] = ReturnNode(p[2])

def p_statement(p):
    '''statement : expression
                    | var_decl
                    | assignment
                    | print'''
    p[0] = p[1]

def p_expression_trivial(p):
    "expression : term"
    p[0] = p[1]

def p_expression_negate(p):
    "expression : '!' term"
    p[0] = NegateExpression(p[2])

def p_expression_negative(p):
    "expression : '-' term %prec UMINUS"
    p[0] = NegativeExpression(p[2])

def p_expression_bool(p):
    '''expression : expression '<' expression
                    | expression '>' expression
                    | expression LESS_OR_EQUAL expression
                    | expression MORE_OR_EQUAL expression
                    | expression STRICT_EQUALS expression
                    | expression STRICT_NOT_EQUAL expression
                    | expression AND expression
                    | expression OR expression
                    '''
    pass

def p_expression_arithm(p):
    '''expression : expression '+' term
                    | expression '-' term'''
    pass

def p_term_trivial(p):
    "term : operand"
    p[0] = p[1]

def p_term(p):
    '''term : term '*' operand
            | term '/' operand'''
    pass

def p_operand_primitive(p):
    "operand : primitive"
    p[0] = PrimitiveValueExpression(p[1])

def p_operand_this(p):
    "operand : THIS"
    p[0] = ThisExpression()

def p_operand_var(p):
    "operand : ID"
    p[0] = VariableExpression(p[1])

def p_operand(p):
    '''operand : function_call
                | new_instance
                | member_access'''
    p[0] = p[1]

def p_primitive_boolean(p):
    '''primitive : TRUE
                | FALSE'''
    value = p[1] == 'true'
    p[0] = BooleanValue(value)

def p_primitive_number(p):
    "primitive : NUMBER"
    p[0] = NumberValue(p[1])

def p_operand_string(p):
    "primitive : STRING"
    p[0] = StringValue(p[1])

def p_primitive_null(p):
    "primitive : NULL"
    p[0] = NullValue()

def p_primitive_undefined(p):
    "primitive : UNDEFINED"
    p[0] = UndefinedValue()

def p_operand_complex(p):
    "operand : '(' expression ')'"
    p[0] = p[2]

def p_member_access(p):
    '''member_access : operand '.' ID
                        | member_access '.' ID'''
    p[0] = MemberAccessessExpression(p[1], p[3])

def p_assignment(p):
    "assignment : ID '=' expression"
    p[0] = VariableAssignmentNode(p[1], p[3])

def p_assignment(p):
    "assignment : var_decl '=' expression"
    p[0] = DeclaredVariableAssignmentNode(p[1], p[3])

def p_assignment_member(p):
    "assignment : member_access '=' expression"
    p[0] = MemberAccessessExpression(p[1], p[3])

def p_if(p):
    '''if : if_no_else
            | if_else'''
    p[0] = p[1]

def p_if_no_else(p):
    "if_no_else : IF '(' expression ')' procedural_item_block"
    p[0] = IfNode(p[3], p[5])

def p_if_else(p):
    "if_else : if_no_else ELSE procedural_item_block"
    p[1].add_else(p[3])
    p[0] = p[1]

def p_loop(p):
    "loop : while_loop"
    p[0] = p[1]

def p_while_loop(p):
    "while_loop : WHILE '(' expression ')' procedural_item_block"
    p[0] = WhileLoopNode(p[3], p[5])

def p_function_decl(p):
    "function_decl : FUNCTION function"
    p[0] = FunctionDeclarationNode(p[2])

def p_function(p):
    "function : ID '(' param_list ')' ':' type language_item_block"
    p[0] = FunctionValue(p[1], p[3], p[6], p[7])

def p_param_list_empty(p):
    "param_list : empty"
    p[0] = []

def p_param_list_one(p):
    "param_list : var"
    p[0] = [p[1]]

def p_param_list(p):
    '''param_list : param_list ',' var '''
    p[1].append(p[3])
    p[0] = p[1]

def p_function_call(p):
    "function_call : ID '(' operand_list ')'"
    p[0] = FunctionCallExpression(p[1], p[3])

def p_operand_list_empty(p):
    "operand_list : empty"
    p[0] = []

def p_operand_list_one(p):
    "operand_list : operand"
    p[0] = [p[1]]

def p_operand_list(p):
    "operand_list : operand_list ',' operand"
    p[1].append(p[3])
    p[0] = p[1]

def p_type(p):
    '''type : ID
            | BOOLEAN_TYPE
            | NUMBER_TYPE
            | STRING_TYPE
            | ANY_TYPE'''
    p[0] = p[1]

def p_var_decl(p):
    "var_decl : LET var"
    p[0] = VariableDeclarationNode(p[2])

def p_var(p):
    "var : ID ':' type"
    p[0] = Variable(p[1], p[3])

def p_class(p):
    "class : CLASS ID '{' member_list '}'"
    p[0] = ClassDeclarationNode(p[2], p[4])

def p_member_list_empty(p):
    "member_list : empty"
    p[0] = []

def p_member_list(p):
    "member_list : member_list member"
    p[1].append(p[2])
    p[0] = p[1]

def p_member(p):
    '''member : var ';'
                | function
                | constructor'''
    p[0] = p[1]

def p_constructor(p):
    "constructor : CONSTRUCTOR '(' param_list ')' language_item_block"
    p[0] = FunctionValue(p[1], p[3], None, p[5])

def p_new_instance(p):
    "new_instance : NEW function_call"
    p[0] = NewInstanceExpression(p[2])

def p_print(p):
    "print : CONSOLE_LOG '(' expression ')'"
    p[0] = PrintNode(p[3])

def p_empty(p):
    'empty : '
    pass

def p_error(p):
    # TODO: it's possible to clarify error based on token type
    if p is None:
        print 'Syntax error: unexpected end of file'
        return
    print "Syntax error on line {}. Unexpected token of type '{}': {}".format(
        p.lineno, p.type, p.value
    )

analyzer = yacc.yacc()
