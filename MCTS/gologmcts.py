import gym
from math import sqrt, log
import random
import pickle
import copy
import numpy as np
import matplotlib.pyplot as plt
from gologenv import *

class GologNode:
    def __init__(self, game, done, parent, observation, action_index, state, depth=0, max_depth=20):
        self.child = None
        self.T = 0
        self.N = 0
        self.game = game
        self.observation = observation
        self.done = done
        self.parent = parent
        self.action_index = action_index
        self.state = copy.deepcopy(state)
        self.depth = depth
        self.max_depth = max_depth

    def getUCBscore(self):
        c = 1.0
        if self.N == 0:
            return float('inf')
        top_node = self
        if top_node.parent:
            top_node = top_node.parent
        return (self.T / self.N) + c * sqrt(log(top_node.N) / self.N)

    def detach_parent(self):
        del self.parent
        self.parent = None

    def create_child(self):
        if self.done or self.depth >= self.max_depth:
            return
        self.child = {}
        for action_index, action in enumerate(self.state.actions):
            new_state = copy.deepcopy(self.state)
            args = [random.choice(domain) for domain in action.arg_domains]
            if action.precondition(new_state, *args):
                new_state.execute_action(action.name, *args)
                new_game = pickle.loads(pickle.dumps(self.game))
                observation, reward, done, _ = new_game.step(action_index)
                self.child[action_index] = GologNode(new_game, done, self, observation, action_index, new_state, self.depth + 1, self.max_depth)

    def explore(self):
        current = self
        while current.child:
            child = current.child
            max_U = max(c.getUCBscore() for c in child.values())
            actions = [a for a, c in child.items() if c.getUCBscore() == max_U]
            action = random.choice(actions)
            current = child[action]
        if current.N < 1:
            current.T += current.rollout()
        else:
            current.create_child()
            if current.child:
                current = random.choice(list(current.child.values()))
            current.T += current.rollout()
        current.N += 1
        parent = current
        while parent.parent:
            parent = parent.parent
            parent.N += 1
            parent.T += current.T

    def rollout(self):
        if self.done or self.depth >= self.max_depth:
            return 0
        v = 0
        done = False
        new_game = pickle.loads(pickle.dumps(self.game))
        depth = self.depth
        while not done and depth < self.max_depth:
            legal_actions = []
            for action in self.state.actions:
                args = [random.choice(domain) for domain in action.arg_domains]
                if action.precondition(self.state, *args):
                    legal_actions.append((action, args))
            if not legal_actions:
                break
            action, args = random.choice(legal_actions)
            new_state = copy.deepcopy(self.state)
            new_state.execute_action(action.name, *args)
            observation, reward, done, _ = new_game.step(self.state.actions.index(action))
            v += reward
            depth += 1
        return v

    def next(self):
        if self.done:
            raise ValueError("game has ended")
        if not self.child:
            raise ValueError('no children found and game hasn\'t ended')
        child = self.child
        max_N = max(node.N for node in child.values())
        max_children = [c for a, c in child.items() if c.N == max_N]
        if not max_children:
            raise ValueError('No valid children to select from.')
        max_child = random.choice(max_children)
        return max_child, max_child.action_index

def Policy_Player_MCTS(mytree, explore_count):
    for i in range(explore_count):
        mytree.explore()
    next_tree, next_action = mytree.next()
    next_tree.detach_parent()
    return next_tree, next_action

# Define the precondition and effect functions to use the current state
def stack_precondition(state, x, y):
    return x != y and x != 'table' and state.fluents[f'loc({x})'].value != y and not any(state.fluents[f'loc({z})'].value == x for z in state.symbols['block'])

def stack_effect(state, x, y):
    state.fluents[f'loc({x})'].set_value(y)

# Initialize the Golog environment
state = GologState()
state.add_symbol('block', ['a', 'b', 'c'])
state.add_symbol('location', ['a', 'b', 'c', 'table'])
state.add_fluent('loc(a)', ['a', 'b', 'c', 'table'], 'c')
state.add_fluent('loc(b)', ['a', 'b', 'c', 'table'], 'table')
state.add_fluent('loc(c)', ['a', 'b', 'c', 'table'], 'b')
stack_action = GologAction('stack', stack_precondition, stack_effect, [state.symbols['block'], state.symbols['location']])
state.add_action(stack_action)

env = GologEnvironment(state)

# Run MCTS with Golog environment
episodes = 10
rewards = []
explore_count = 100

for e in range(episodes):
    reward_e = 0
    game = pickle.loads(pickle.dumps(env))
    observation = game.reset()
    done = False
    mytree = GologNode(game, False, None, observation, None, state, max_depth=20)

    print('Episode #' + str(e+1) + "+====================================+")
    actions_taken = []
    while not done:
        try:
            mytree, action = Policy_Player_MCTS(mytree, explore_count)
            specific_args = [random.choice(domain) for domain in mytree.state.actions[action].arg_domains]
            actions_taken.append((mytree.state.actions[action].name, specific_args))
            observation, reward, done, _ = game.step(action)
            reward_e += reward
            game.render()
        except ValueError as ve:
            print(ve)
            # Handle the situation where no valid children are found
            break
        if done:
            print('Total reward:', reward_e)
            print('Actions taken:', actions_taken)
            game.close()
            break

    rewards.append(reward_e)

plt.plot(rewards)
plt.show()