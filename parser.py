## AST tools

from core import (
    ASTNode, StructSymbol, Scope, VariableSymbol,
    FunctionSymbol, LocalScope
)

## lex ##

import ply.lex as lex

keywords = (
    'DEFSTRUCT', 'DEFUN', 'END', 'EQUALS', 'DOT', 'NEW', 'PRINT',
    'RETURN'
)

tokens = keywords + (
    'ID', 'COLON', 'COMMA', 'STRING', 'INT', 'LPAREN', 'RPAREN'
)

t_ignore = ' \t\n'  # ignoring newlines

t_COMMA = r'\,'
t_COLON = r'\:'
t_EQUALS = r'='
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r"'([^\\']+|\\'|\\\\)*'"
    t.value = t.value[1:-1].decode("string-escape")
    return t

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    print "Skipping", repr(t.value[0])
    t.lexer.skip(1)

def t_ID(t):
    r'[A-Za-z_][\w_]*'
    t.type = reserved_map.get(t.value, "ID")
    return t

reserved_map = { }
for r in keywords:
    reserved_map[r.lower()] = r

lex.lex(debug=0)

current_scope = Scope()

## parse ##

import ply.yacc as yacc

def p_program(p):
    '''program : program program_unit
               | program_unit
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1], p[2]]

def p_program_unit(p):
    '''program_unit : statement
                    | function_definition
    '''
    p[0] = p[1]

def p_statement(p):
    '''statement : struct_definition
                 | assign
                 | print
                 | call
                 | return'''
    p[0] = p[1]

def p_statement_structdef(p):
    '''struct_definition : DEFSTRUCT ID COLON id_list END'''
    global current_scope
    ss = StructSymbol(p[2], current_scope)
    current_scope.define(ss)
    current_scope = ss
    for varsym in p[4]:
        vs = VariableSymbol(varsym)
        current_scope.define(vs)
    current_scope = current_scope.enclosing_scope

def p_function_definition(p): # TODO: refactor this 
    '''function_definition : DEFUN ID paren_id_list COLON program END
                           | DEFUN ID paren_empty_list COLON program END'''
    global current_scope
    fs = FunctionSymbol(p[2], current_scope)
    current_scope.define(fs)
    current_scope = fs
    for varsym in p[3]:
        vs = VariableSymbol(varsym)
        current_scope.define(vs)
    current_scope = LocalScope(fs)
    fs.ast_block = p[5] if isinstance(p[5], list) else [p[5]]
    current_scope = current_scope.enclosing_scope # why do we need twice?
    current_scope = current_scope.enclosing_scope

def p_paren_id_list(p):
    '''paren_id_list : LPAREN id_list RPAREN'''
    p[0] = p[2] if isinstance(p[2], list) else [p[2]]

def p_paren_expr_list(p):
    '''paren_expr_list : LPAREN expr_list RPAREN'''
    p[0] = p[2] if isinstance(p[2], list) else [p[2]]

def p_paren_empty_list(p):
    '''paren_empty_list : LPAREN RPAREN'''
    p[0] = []

def p_call(p): # TODO: refactor this
    '''call : ID paren_expr_list
            | ID paren_empty_list'''
    node = ASTNode('CALL', children=[p[1], p[2]])
    node.scope = current_scope
    p[0] = node

def p_assign(p):
    '''assign : qid EQUALS expr'''
    p[0] = ASTNode('ASSIGN', children=[p[1], p[3]])

def p_return(p):
    '''return : RETURN expr'''
    p[0] = ASTNode('RET', leaf=p[2])

def p_print(p):
    '''print : PRINT expr'''
    p[0] = ASTNode('PRINT', leaf=p[2])

def p_qid(p):
    '''qid : ID
           | qid DOT ID'''
    if len(p) == 2:
        p[0] = ASTNode('ID', leaf=p[1])
    else:
        if p[1].type == 'ID':
            p[0] = ASTNode('QID', leaf=p[1].leaf+'.'+p[3])
        else:
            p[1].leaf = p[1].leaf+'.'+p[3]
            p[0] = p[1]

def p_id_list(p):
    '''id_list : ID
               | id_list COMMA ID'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1], p[3]]

def p_expr_list(p):
    '''expr_list : expr
                 | expr_list COMMA expr'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1], p[3]]

def p_instance(p):
    '''instance : NEW ID'''
    global current_scope
    node = ASTNode('INSTANCE', leaf=p[2])
    node.scope = current_scope
    p[0] = node

def p_expr(p):
    '''expr : atom'''
    p[0] = p[1]

def p_atom(p):
    '''atom : string
            | int
            | instance
            | qid
            | call'''
    p[0] = p[1]

def p_string(p):
    ''' string : STRING'''
    p[0] = ASTNode('STRING', leaf=p[1])

def p_int(p):
    ''' int : INT'''
    p[0] = ASTNode('INT', leaf=p[1])

def p_error(p):
    if not p:
        print("Syntax Error at EOF")
    else:
        print 'Syntax Error on {0}'.format(p)

parser = yacc.yacc()

def parse(data, debug=0):
    parser.error = 0
    p = parser.parse(data, debug=debug)
    if parser.error:
        return None
    return p

code_sample = """
defstruct BaseResource:
  target, call, args
end

example = new BaseResource
example.target = 'hello'

print example
"""

if __name__ == ('__main__'):
    print [str(a) for a in parser.parse(code_sample)]
    
    
