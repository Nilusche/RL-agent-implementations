from gologenv import GologState, GologAction, GologEnvironment
from copy import deepcopy
from gologmcts import GologNode, Policy_Player_MCTS
from gologparser import parser, parsed_elements

def create_environment_from_parsed_elements(parsed_elements):
    initial_state = GologState()
    
    # Add symbols
    for symbol, domain in parsed_elements['symbols'].items():
        initial_state.add_symbol(symbol, domain)
    
    # Add fluents
    for fluent, values in parsed_elements['fluents'].items():
        initial_state.add_fluent(fluent, initial_state.symbols['block'], values[list(values.keys())[0]])

    # Add actions
    actions = []
    for action_name, args, precondition, effect in parsed_elements['actions']:
        def make_precondition(precondition):
            def precond(state, *args):
                # Add logic to check preconditions
                return eval(precondition.replace('&', 'and').replace('|', 'or'))
            return precond

        def make_effect(effect):
            def eff(state, *args):
                # Add logic to apply effects
                setattr(state.fluents[f"loc({args[0]})"], 'value', args[1])
            return eff

        action = GologAction(action_name, make_precondition(precondition), make_effect(effect), args)
        actions.append(action)
        initial_state.add_action(action)
    
    # Goal function
    def goal_function(state):
        return eval(parsed_elements['goal'][1].replace('&', 'and').replace('|', 'or'))

    # Reward function
    def reward_function(state):
        condition, if_reward, else_reward = parsed_elements['reward'][1]
        if eval(condition.replace('&', 'and').replace('|', 'or')):
            return if_reward
        return else_reward

    env = GologEnvironment(initial_state, goal_function, actions, reward_function)
    return env

def run_procedure(env, procedure_name):
    procedure = parsed_elements['procedures'].get(procedure_name)
    if not procedure:
        print(f"Procedure {procedure_name} not found.")
        return

    for stmt in procedure:
        if stmt[0] == 'action':
            action_name, args = stmt[1], stmt[2]
            action_index = next(i for i, a in enumerate(env.actions) if a.name == action_name)
            env.step((action_index, args))
            env.render()
        elif stmt[0] == 'mcts':
            iterations, reward_function_name = stmt[1], stmt[2]
            print(f"Running MCTS with {iterations} iterations")
            goal_function = env.goal_function
            reward_function = env.reward_function

            new_game = deepcopy(env)
            mytree = GologNode(new_game, None, False, env._get_observation(), 0)

            for _ in range(iterations):
                mytree.explore()
            
            best_action = mytree.next()
            if best_action:
                action_index, args = best_action[1], best_action[2]
                env.step((action_index, args))
                env.render()
