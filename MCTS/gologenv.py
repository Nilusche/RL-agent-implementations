import gym
from gym import spaces
import random
import copy

class Fluent:
    def __init__(self, name, domain, initial_value):
        self.name = name
        self.domain = domain
        self.value = initial_value

    def set_value(self, new_value):
        if new_value in self.domain:
            self.value = new_value
        else:
            raise ValueError(f"Value {new_value} not in domain {self.domain}")

    def get_value_index(self):
        return self.domain.index(self.value)

class GologState:
    def __init__(self):
        self.symbols = {}
        self.actions = []
        self.fluents = {}

    def add_symbol(self, symbol, domain):
        self.symbols[symbol] = domain

    def add_fluent(self, name, domain, initial_value):
        self.fluents[name] = Fluent(name, domain, initial_value)

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
    def __init__(self, state):
        super(GologEnvironment, self).__init__()
        self.initial_state = copy.deepcopy(state)
        self.state = copy.deepcopy(state)
        self.action_space = spaces.Discrete(len(state.actions))
        self.observation_space = self._get_observation_space()
        self.done = False
        self.info = {}

    def reset(self):
        self.state = copy.deepcopy(self.initial_state)
        self.done = False
        self.info = {}
        return self._get_observation()

    def step(self, action_index):
        action = self.state.actions[action_index]
        args = [random.choice(domain) for domain in action.arg_domains]
        print(f"Executing action: {action.name} with arguments {args}")
        action_executed = self.state.execute_action(action.name, *args)
        observation = self._get_observation()
        reward = self._calculate_reward()
        self.done = self.goal_condition()
        return observation, reward, self.done, self.info

    def _get_observation_space(self):
        observation_space = {}
        for fluent in self.state.fluents.values():
            observation_space[fluent.name] = spaces.Discrete(len(fluent.domain))
        return spaces.Dict(observation_space)

    def _get_observation(self):
        observation = {}
        for fluent in self.state.fluents.values():
            observation[fluent.name] = fluent.get_value_index()
        return observation

    def _calculate_reward(self):
        if self.goal_condition():
            return 100
        else:
            return -1

    def goal_condition(self):
        return self.state.fluents['loc(a)'].value == 'table' and \
               self.state.fluents['loc(b)'].value == 'a' and \
               self.state.fluents['loc(c)'].value == 'b'

    def observation_to_state(self, observation):
        state = {}
        for fluent_name, index in observation.items():
            state[fluent_name] = self.state.fluents[fluent_name].domain[index]
        return state

    def state_to_observation(self, state):
        observation = {}
        for fluent_name, value in state.items():
            observation[fluent_name] = self.state.fluents[fluent_name].domain.index(value)
        return observation

# Define the precondition and effect functions to use the current state
def stack_precondition(state, x, y):
    return x != y and x != 'table' and state.fluents[f'loc({x})'].value != y and not any(state.fluents[f'loc({z})'].value == x for z in state.symbols['block'])

def stack_effect(state, x, y):
    state.fluents[f'loc({x})'].set_value(y)

# Initialize the GologState for Blocksworld
state = GologState()
state.add_symbol('block', ['a', 'b', 'c'])
state.add_symbol('location', ['a', 'b', 'c', 'table'])

state.add_fluent('loc(a)', ['a', 'b', 'c', 'table'], 'c')
state.add_fluent('loc(b)', ['a', 'b', 'c', 'table'], 'table')
state.add_fluent('loc(c)', ['a', 'b', 'c', 'table'], 'b')

# Create the stack action
stack_action = GologAction('stack', stack_precondition, stack_effect, [state.symbols['block'], state.symbols['location']])
state.add_action(stack_action)

# Initialize the GologEnvironment
env = GologEnvironment(state)

# Example usage with a random policy
observation = env.reset()
print("Initial Observation:", observation)
state = env.observation_to_state(observation)
print("Initial State:", state)
done = False
while not done:
    action_index = env.action_space.sample()  # Randomly sample an action index
    print("Selected Action Index:", action_index)
    observation, reward, done, info = env.step(action_index)
    print("Observation:", observation)
    print("State:", env.observation_to_state(observation))
    print("Reward:", reward)
    print("Done:", done)
