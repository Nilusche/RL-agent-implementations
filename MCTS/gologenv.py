import gym
from gym import spaces
import random
import copy
from collections import deque
from math import sqrt, log
import pickle

class GologFluent:
    def __init__(self, domain, value):
        self.domain = domain
        self.value = value

    def set_value(self, value):
        if value in self.domain:
            self.value = value

    def __repr__(self):
        return str(self.value)

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

    def __hash__(self):
        return hash(frozenset((fluent, fl.value) for fluent, fl in self.fluents.items()))

    def __eq__(self, other):
        return all(self.fluents[fluent].value == other.fluents[fluent].value for fluent in self.fluents)

class GologAction:
    def __init__(self, name, precondition, effect, arg_domains):
        self.name = name
        self.precondition = precondition
        self.effect = effect
        self.arg_domains = arg_domains

class GologEnvironment(gym.Env):
    def __init__(self, initial_state, goal_function, reward_function=None):
        super(GologEnvironment, self).__init__()
        self.initial_state = initial_state
        self.state = copy.deepcopy(initial_state)
        self.goal_function = goal_function
        self.reward_function = reward_function if reward_function else self.default_reward_function
        self.action_space = spaces.Discrete(len(initial_state.actions))
        self.observation_space = spaces.Discrete(len(initial_state.fluents))
        self.done = False
        self.reset()

    def reset(self):
        # Reset to initial state
        self.done = False
        self.state = copy.deepcopy(self.initial_state)
        return self._get_observation()
    
    def _get_observation(self):
        observation = {}
        for fluent in self.state.fluents:
            observation[fluent] = self.state.fluents[fluent].value
        return observation

    def step(self, action):
        action_index, args = action
        action = self.state.actions[action_index]
        if action.precondition(self.state, *args):
            action.effect(self.state, *args)
            reward = self.reward_function(self.state)
            self.done = self.goal_function(self.state)
            return self._get_observation(), reward, self.done, {}
        else:
            return self._get_observation(), -1, self.done, {}

    def default_reward_function(self, state):
        return 100 if self.goal_function(state) else -1

    def render(self, mode='human'):
        state_description = []
        for fluent, value in self.state.fluents.items():
            state_description.append(f"{fluent} is {value.value}")
        print("Current State:")
        print("\n".join(state_description))
