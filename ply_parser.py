import ply.lex as lex
import ply.yacc as yacc
import math
import tree

from graphviz import Digraph


tokens = (
    "INTEGER",
    "FLOAT",
    "RELATION",
    "IF",
    "WHILE",
    "FOR",
    "FUNCTION",
    "NAME",
    "STRING",
    "BOOL",
    "PRINT",
    "TVASSIGNMENT",
    "CAST",
    "TYPE_NAME",
    "MATH_FUNCTION",
    "COMMENT",
    "PI",
)

literals = ["=", "+", "-", "*", "/", "(", ")", ";", ":", "^", "{", "}", ","]


def t_FLOAT(t):
    r"\d+\.\d+|\.\d+"
    return t


def t_INTEGER(t):
    r"\d+"
    return t


def t_BOOL(t):
    r"true|false"
    return t


def t_CAST(t):
    r"static_cast"
    return t


def t_IF(t):
    r"if"
    return t


def t_WHILE(t):
    r"while"
    return t


def t_FOR(t):
    r"for"
    return t


def t_FUNCTION(t):
    r"function"
    return t


def t_PRINT(t):
    r"print"
    return t


def t_TYPE_NAME(t):
    r"int|float|string|bool"
    return t


def t_MATH_FUNCTION(t):
    r"sin|cos|exp|sqrt|log"
    return t


def t_TWOSTAR(t):
    r"\*\*"
    t.type = "^"
    t.value = "^"
    return t


def t_PI(t):
    r"PI"
    return t


def t_COMMENT(t):
    r"\#.*"
    return t


def t_STRING(t):
    r"\"(.*?)\""
    return t


def t_NAME(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_RELATION = r"<=|>=|==|!=|<|>"

t_TVASSIGNMENT = r":="

t_ignore = " \t"

precedence = (
    ("left", "RELATION"),
    ("left", "+", "-"),
    ("left", "*", "/"),
    ("right", "^"),
)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def p_program(p):
    " program   : block"
    p[0] = tree.Program(p[1])


def p_block(p):
    """ block   : statement block
                | statement """
    statements = []

    statements.append(p[1])
    if len(p) > 2:
        for statement in p[2].get_statements():
            statements.append(statement)

    p[0] = tree.Block(statements)


def p_statement_instruction_block(p):
    " statement : '{' block '}'"
    p[0] = tree.InstructionBlock(p[2])


def p_statement_comment(p):
    " statement : COMMENT "
    p[0] = tree.Comment(p[0])


def p_statement_print(p):
    " statement : PRINT '(' statement ')' "
    p[0] = tree.Print(p[3])


def p_statement_condition(p):
    " statement : IF '(' statement ')' '{' block '}' "
    p[0] = tree.Condition(p[3], p[6])


def p_statement_while(p):
    " statement : WHILE '(' statement ')' '{' block '}' "
    p[0] = tree.While(p[3], p[6])


def p_statement_for(p):
    " statement : FOR '(' statement ';' statement ';' statement ')' '{' block '}'"
    p[0] = tree.For(p[3], p[5], p[7], p[10])


def p_statement_assignment(p):
    "statement : NAME '=' statement "
    p[0] = tree.Assign(tree.NameVal(p[1]), p[3])


def p_statement_type_declaration(p):
    "statement : arg_tuple"
    p[0] = tree.TypeDeclare(tree.NameVal(p[1][0]), tree.TypeVal(p[1][1]))


def p_statement_type_value_assignment(p):
    "statement : NAME TVASSIGNMENT statement"
    p[0] = tree.AssignWithType(tree.NameVal(p[1]), p[3])


def p_statement_function(p):
    " statement : FUNCTION NAME '(' args ')' '=' '{' block '}'"
    p[0] = tree.Function(tree.NameVal(p[2]), p[4], p[8])


def p_statement_no_args_function(p):
    " statement : FUNCTION NAME '(' ')' '=' '{' block '}'"
    p[0] = tree.Function(tree.NameVal(p[2]), None, p[7])


def p_statement_expr(p):
    """ statement   : expression
                    | relation """
    p[0] = p[1]


def p_args(p):
    """ args    : arg_tuple ',' args
                | arg_tuple """
    args = []

    args.append((tree.NameVal(p[1][0]), tree.TypeVal(p[1][1])))
    if "," in p[1:]:
        for argument in p[3].get_arguments():
            args.append(argument)

    p[0] = tree.Args(args)


def p_arg_tuple(p):
    " arg_tuple : NAME ':' TYPE_NAME"
    p[0] = (p[1], p[3])


def p_args_val(p):
    """ args_val    : expression ',' args_val
                    | expression """
    args = []

    args.append(p[1])
    if "," in p[1:]:
        for argument in p[3].get_arguments():
            args.append(argument)

    p[0] = tree.ArgsVal(args)


def p_binary_operators(p):
    """  expression : expression '+' expression
                    | expression '-' expression
                    | expression '*' expression
                    | expression '/' expression
                    | expression '^' expression  """
    p[0] = tree.Operator(p[2], p[1], p[3])


def p_math_function(p):
    " expression : MATH_FUNCTION '(' expression ')' "
    p[0] = tree.MathFunction(p[1], p[3])


def p_relation_operators(p):
    "  relation : expression RELATION expression "
    p[0] = tree.Relation(p[2], p[1], p[3])


"""
def p_unary_minus(p):
    " expression : '-' expression"
    p[0] = tree.UMinus(p[2])
"""


def p_expression_cast(p):
    " expression : CAST '(' statement ',' TYPE_NAME ')'"
    p[0] = tree.Cast(p[3], tree.TypeVal(p[5]))


def p_expression_call(p):
    " expression : NAME '(' args_val ')' "
    p[0] = tree.Call(tree.NameVal(p[1]), p[3])


def p_expression_call_no_args(p):
    " expression : NAME '(' ')' "
    p[0] = tree.Call(tree.NameVal(p[1]), None)


def p_expression_float(p):
    " expression : FLOAT"
    p[0] = tree.FloatVal(p[1])


def p_expression_integer(p):
    " expression : INTEGER"
    p[0] = tree.IntVal(p[1])


def p_expression_name(p):
    " expression : NAME "
    p[0] = tree.KeyVal(p[1])


def p_expression_string(p):
    " expression : STRING"
    p[0] = tree.StringVal(p[1])


def p_expression_bool(p):
    " expression : BOOL"
    p[0] = tree.BoolVal(p[1])


def p_expression_pi(p):
    " expression : PI"
    p[0] = tree.Pi()


def p_error(p):
    if p:
        print(f"Syntax error at token {p.value}.")
        parser.errok()
    else:
        print("Syntax error at EOF")


def parse_file(path, verbose=False):
    with open(path, "r") as f:
        content = f.read()

        parse(content, False, verbose)


def parse_cmd(hide_tree=False, verbose=False):
    while True:
        try:
            s = input("> ")
        except EOFError:
            break
        if not s:
            continue

        parse(s, hide_tree, verbose)


def parse(content, hide_tree, verbose):
    lexer = lex.lex()
    parser = yacc.yacc()

    if verbose:
        print_tokens(lexer, content)

    ast = None
    ast = yacc.parse(content)

    if ast is not None:
        ast = ast.optimize()
        ast.serve()

        graph = Digraph()
        ast.draw(graph)
        if not hide_tree:
            graph.render("ast", format="png", view=True, cleanup=True)


def print_tokens(lexer, content):
    print("-------------------------TOKENS----------------------------")
    print("-----------------------------------------------------------")
    # Give the lexer some input
    lexer.input(content)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)

    print("-----------------------------------------------------------")
    print("--------------------INTERPRETATION-------------------------\n")
