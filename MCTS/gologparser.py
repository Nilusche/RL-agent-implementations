import ply.yacc as yacc
from gologlex import tokens

parsed_elements = {
    'symbols': {},
    'fluents': {},
    'actions': [],
    'procedures': {},
    'goal': None,
    'reward': None,
    'postcond': None
}

def p_program(p):
    '''program : symbol_defs fluent_defs action_defs procedure_defs functions'''
    p[0] = parsed_elements

def p_symbol_defs(p):
    '''symbol_defs : symbol_def symbol_defs
                   | symbol_def
                   | empty'''
    pass

def p_symbol_def(p):
    '''symbol_def : SYMBOL DOMAIN ID EQ LBRACE id_list RBRACE SEMI
                  | SYMBOL DOMAIN ID EQ ID OR LBRACE id_list RBRACE SEMI'''
    if len(p) == 9:
        parsed_elements['symbols'][p[3]] = p[6]
    else:
        parsed_elements['symbols'][p[3]] = [p[5]] + p[8]

def p_id_list(p):
    '''id_list : ID COMMA id_list
               | ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_fluent_defs(p):
    '''fluent_defs : fluent_def fluent_defs
                   | fluent_def
                   | empty'''
    pass

def p_fluent_def(p):
    '''fluent_def : LOCATION FLUENT LOC LPAREN ID RPAREN LBRACE initial_values RBRACE'''
    fluent_name = f"loc({p[5]})"
    parsed_elements['fluents'][fluent_name] = p[8]

def p_initial_values(p):
    '''initial_values : INITIAL LBRACE fluent_values RBRACE'''
    p[0] = p[3]

def p_fluent_values(p):
    '''fluent_values : LPAREN ID RPAREN EQ ID SEMI fluent_values
                     | LPAREN ID RPAREN EQ ID SEMI'''
    if len(p) == 7:
        p[0] = {p[2]: p[5]}
    else:
        p[0] = {p[2]: p[5]}
        p[0].update(p[7])

def p_action_defs(p):
    '''action_defs : action_def action_defs
                   | action_def
                   | empty'''
    pass

def p_action_def(p):
    '''action_def : ACTION ID LPAREN ID COMMA ID RPAREN LBRACE precondition effect RBRACE'''
    action_name = p[2]
    args = (p[4], p[6])
    parsed_elements['actions'].append((action_name, args, p[8], p[9]))

def p_precondition(p):
    '''precondition : PRECONDITION COLON condition'''
    p[0] = p[3]

def p_condition(p):
    '''condition : condition AND condition
                 | condition OR condition
                 | NOT condition
                 | EXISTS LPAREN ID ID RPAREN condition
                 | ID NEQ ID
                 | ID EQ ID'''
    p[0] = p[1:]

def p_effect(p):
    '''effect : EFFECT COLON effect_action SEMI'''
    p[0] = p[3]

def p_effect_action(p):
    '''effect_action : ID LPAREN ID RPAREN EQ ID'''
    p[0] = (p[1], p[3], p[6])

def p_procedure_defs(p):
    '''procedure_defs : procedure_def procedure_defs
                      | procedure_def
                      | empty'''
    pass

def p_procedure_def(p):
    '''procedure_def : PROCEDURE ID LBRACE procedure_body RBRACE'''
    parsed_elements['procedures'][p[2]] = p[4]

def p_procedure_body(p):
    '''procedure_body : statement procedure_body
                      | statement'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : action_call
                 | mcts_call'''
    p[0] = p[1]

def p_action_call(p):
    '''action_call : ID LPAREN ID COMMA ID RPAREN SEMI'''
    p[0] = ('action', p[1], (p[3], p[5]))

def p_mcts_call(p):
    '''mcts_call : MCTS LPAREN NUMBER COMMA ID RPAREN SEMI'''
    p[0] = ('mcts', p[3], p[5])

def p_functions(p):
    '''functions : bool_function number_function'''
    pass

def p_bool_function(p):
    '''bool_function : BOOL_FUNCTION ID EQ condition SEMI'''
    parsed_elements['goal'] = (p[2], p[4])

def p_number_function(p):
    '''number_function : NUMBER_FUNCTION ID EQ reward_function SEMI'''
    parsed_elements['reward'] = (p[2], p[4])

def p_reward_function(p):
    '''reward_function : IF LPAREN condition RPAREN NUMBER ELSE NUMBER'''
    p[0] = (p[3], p[5], p[7])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    print(f"Syntax error at '{p.value}'")

parser = yacc.yacc()
