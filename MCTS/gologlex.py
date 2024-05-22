import ply.lex as lex

tokens = (
    'SYMBOL', 'DOMAIN', 'BLOCK', 'LOCATION', 'FLUENT', 'ACTION',
    'PROCEDURE', 'BOOL_FUNCTION', 'NUMBER_FUNCTION', 'IF', 'ELSE',
    'WHILE', 'PICK', 'INITIAL', 'LOC', 'AND', 'OR', 'EXISTS',
    'GOAL', 'REWARD', 'POSTCOND', 'MCTS', 'BFS', 'ID', 'NUMBER',
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'SEMI', 'COMMA', 'EQ',
    'NEQ', 'LT', 'GT', 'LTE', 'GTE', 'NOT', 'COLON', 'PRECONDITION', 'EFFECT', 'COMMENT'
)

t_SYMBOL = r'symbol'
t_DOMAIN = r'domain'
t_BLOCK = r'block'
t_LOCATION = r'location'
t_FLUENT = r'fluent'
t_ACTION = r'action'
t_PROCEDURE = r'procedure'
t_BOOL_FUNCTION = r'bool\sfunction'
t_NUMBER_FUNCTION = r'number\sfunction'
t_IF = r'if'
t_ELSE = r'else'
t_WHILE = r'while'
t_PICK = r'pick'
t_INITIAL = r'initially'
t_LOC = r'loc'
t_AND = r'\&'
t_OR = r'\|'
t_EXISTS = r'exists'
t_GOAL = r'goal'
t_REWARD = r'reward'
t_POSTCOND = r'postcond'
t_MCTS = r'mcts'
t_BFS = r'bfs'
t_EQ = r'='
t_NEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_NOT = r'!'
t_COLON = r':'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMI = r';'
t_COMMA = r','
t_PRECONDITION = r'precondition'
t_EFFECT = r'effect'
t_COMMENT = r'//.*'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()
