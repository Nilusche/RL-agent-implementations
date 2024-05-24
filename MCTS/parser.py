from lark import Lark, Transformer, v_args
from gologenv import GologState, GologAction, GologEnvironment

golog_grammar = """
?start: statement*

?statement: symbol_definition
          | fluent_definition
          | action_definition
          | procedure_definition
          | goal_definition
          | reward_definition
          | main_procedure

symbol_definition: "symbol domain" SYMBOL "=" "{" SYMBOL_LIST "}"
fluent_definition: "location fluent" FLUENT "(" SYMBOL ")" "{" "initially:" INITIAL_VALUES "}"
action_definition: "action" ACTION "(" PARAM_LIST ")" "{" "precondition:" CONDITION "effect:" EFFECT "}"
procedure_definition: "procedure" PROCEDURE "()" "{" ACTION_LIST "}"
goal_definition: "bool function goal()" "=" CONDITION
reward_definition: "number function reward()" "=" REWARD_CONDITION
main_procedure: "procedure main()" "{" MAIN_ACTION "}"

SYMBOL: /[a-zA-Z_]\w*/
SYMBOL_LIST: SYMBOL ("," SYMBOL)*
FLUENT: /[a-zA-Z_]\w*/
INITIAL_VALUES: "(" SYMBOL ")" "=" SYMBOL (";" "(" SYMBOL ")" "=" SYMBOL)*
ACTION: /[a-zA-Z_]\w*/
PARAM_LIST: PARAM ("," PARAM)*
PARAM: SYMBOL SYMBOL
CONDITION: /[^;]+/
EFFECT: /[^;]+/
PROCEDURE: /[a-zA-Z_]\w*/
ACTION_LIST: ACTION_CALL (";" ACTION_CALL)*
ACTION_CALL: SYMBOL "(" SYMBOL ("," SYMBOL)* ")"
REWARD_CONDITION: "if (" CONDITION ")" "100" "else" "-1"
MAIN_ACTION: SYMBOL "(" NUMBER "," SYMBOL ")"

%import common.NUMBER
%import common.WS
%ignore WS
"""

class GologTransformer(Transformer):
    def __init__(self):
        self.symbols = {}
        self.fluents = []
        self.actions = []
        self.procedures = {}
        self.goal = None
        self.reward = None
        self.main_procedure = []

    def symbol_definition(self, args):
        name = str(args[0])
        values = [str(value) for value in args[1:]]
        self.symbols[name] = values

    def fluent_definition(self, args):
        name = str(args[0])
        symbol = str(args[1])
        initial_values = [(str(x[0]), str(x[1])) for x in zip(args[2::2], args[3::2])]
        self.fluents.append({'name': name, 'symbol': symbol, 'initial_values': initial_values})

    def action_definition(self, args):
        name = str(args[0])
        params = [str(param) for param in args[1:]]
        precondition = str(args[-2])
        effect = str(args[-1])
        self.actions.append({'name': name, 'params': params, 'precondition': precondition, 'effect': effect})

    def procedure_definition(self, args):
        name = str(args[0])
        actions = [str(action) for action in args[1:]]
        self.procedures[name] = actions

    def goal_definition(self, args):
        self.goal = str(args[0])

    def reward_definition(self, args):
        self.reward = str(args[0])

    def main_procedure(self, args):
        self.main_procedure = [str(action) for action in args]

    def get_environment(self):
        initial_state = GologState()

        for symbol, domain in self.symbols.items():
            initial_state.add_symbol(symbol, domain)

        for fluent in self.fluents:
            for (block, loc) in fluent['initial_values']:
                initial_state.add_fluent(f'{fluent["name"]}({block})', initial_state.symbols[fluent['symbol']], loc)

        actions = []
        for action in self.actions:
            precondition_code = compile(action['precondition'].strip(), '<string>', 'exec')
            effect_code = compile(action['effect'].strip(), '<string>', 'exec')

            def make_precondition(precondition_code):
                def precondition(state, x, y):
                    locals().update(state.fluents)
                    exec(precondition_code)
                    return eval('result')
                return precondition

            def make_effect(effect_code):
                def effect(state, x, y):
                    locals().update(state.fluents)
                    exec(effect_code)
                return effect

            precondition = make_precondition(precondition_code)
            effect = make_effect(effect_code)

            actions.append(GologAction(action['name'], precondition, effect, [initial_state.symbols[param.split()[1]] for param in action['params']]))

        initial_state.actions.extend(actions)

        goal_code = compile(self.goal, '<string>', 'eval')
        def goal_function(state):
            locals().update(state.fluents)
            return eval(goal_code)

        reward_code = compile(self.reward, '<string>', 'eval')
        def reward_function(state):
            locals().update(state.fluents)
            return eval(reward_code)

        env = GologEnvironment(initial_state, goal_function, actions, reward_function)
        return env

parser = Lark(golog_grammar, parser='lalr', transformer=GologTransformer())
