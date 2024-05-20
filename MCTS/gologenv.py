import gym
from gym import spaces
import random
import copy

class GologFluent:
    def __init__(self, domain, value):
        self.domain = domain
        self.value = value

    def set_value(self, value):
        if value in self.domain:
            self.value = value

class GologState:
    def __init__(self):
        self.symbols = {}
        self.actions = []
        self.fluents = {}

    def add_symbol(self, symbol, domain):
        self.symbols[symbol] = domain
    
    def add_fluent(self, fluent, domain, initial_value):
        self.fluents[fluent] = GologFluent(domain, initial_value)

    def add_action(self, action):
        self.actions.append(action)
    
    def execute_action(self, action_name, *args):
        for action in self.actions: 
            if action.name == action_name:
                if action.precondition(self, *args):
                    action.effect(self, *args)
                    return True
        return False

class GologAction:
    def __init__(self, name, precondition, effect, arg_domains):
        self.name = name
        self.precondition = precondition
        self.effect = effect
        self.arg_domains = arg_domains

class GologEnvironment(gym.Env):
    def __init__(self, state, goal_function):
        super(GologEnvironment, self).__init__()
        self.state = state
        self.goal_function = goal_function
        self.action_space = spaces.Discrete(len(state.actions))
        self.observation_space = spaces.Discrete(len(state.fluents))
        self.done = False
        self.initial_state = copy.deepcopy(state)
        self.reset()

    def reset(self):
        self.done = False
        self.state = copy.deepcopy(self.initial_state)
        return self._get_observation()
    
    def _get_observation(self):
        observation = {}
        for fluent in self.state.fluents:
            observation[fluent] = self.state.fluents[fluent].value
        return observation

    def step(self, action_with_args):
        action_index, args = action_with_args
        action = self.state.actions[action_index]
        if action.precondition(self.state, *args):
            action.effect(self.state, *args)
            reward = 100 if self.goal_function(self.state) else -1
            self.done = self.goal_function(self.state)
            return self._get_observation(), reward, self.done, {}
        else:
            return self._get_observation(), -1, self.done, {}

    def render(self, mode='human'):
        state_description = []
        for fluent, value in self.state.fluents.items():
            state_description.append(f"{fluent} is {value.value}")
        print("Current State:")
        print("\n".join(state_description))


# Define the precondition and effect functions to use the current state
# def stack_precondition(state, x, y):
#     return x != y and x != 'table' and state.fluents[f'loc({x})'].value != y and not any(state.fluents[f'loc({z})'].value == x for z in state.symbols['block'])

# def stack_effect(state, x, y):
#     state.fluents[f'loc({x})'].set_value(y)

# def blocksworld_goal(state):
#     return state.fluents['loc(a)'].value == 'table' and state.fluents['loc(b)'].value == 'a' and state.fluents['loc(c)'].value == 'b'

# # Initialize the GologState for Blocksworld
# state = GologState()
# state.add_symbol('block', ['a', 'b', 'c'])
# state.add_symbol('location', ['a', 'b', 'c', 'table'])

# state.add_fluent('loc(a)', ['a', 'b', 'c', 'table'], 'c')
# state.add_fluent('loc(b)', ['a', 'b', 'c', 'table'], 'table')
# state.add_fluent('loc(c)', ['a', 'b', 'c', 'table'], 'b')

# # Create the stack action
# stack_action = GologAction('stack', stack_precondition, stack_effect, [state.symbols['block'], state.symbols['location']])
# state.add_action(stack_action)

# # Initialize the GologEnvironment
# env = GologEnvironment(state, blocksworld_goal)

# done = False
# while not done:
#     action_index = env.action_space.sample()  # Randomly sample an action index
    
    
#     observation, reward, done, info = env.step(action_index)
#     env.render()
