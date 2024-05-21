from math import sqrt, log
from copy import deepcopy
import random
import pickle
from gologenv import *


class GologNode:
    def __init__(self, game, parent, done, observation, action_index, args=None):
        self.child = None
        self.T = 0
        self.N = 0
        self.game = game
        self.observation = observation
        self.done = done
        self.parent = parent
        self.action_index = action_index
        self.args = args  # Ensure args is an attribute

    def get_UCB_score(self, c=1.0):
        if self.N == 0:
            return float('inf')
        top_node = self
        if top_node.parent:
            top_node = top_node.parent 
        
        return self.T / self.N + c * sqrt(log(top_node.N) / self.N)

    def detach_parent(self):
        del self.parent
        self.parent = None

    def create_child(self):
        if self.done:
            return
    
        actions = []
        games = []
        for i in range(self.game.action_space.n): 
            actions.append(i)           
            new_game = copy.deepcopy(self.game)
            games.append(new_game)
            
        child = {} 
        for action, game in zip(actions, games):
            for block in game.state.symbols['block']:
                for location in game.state.symbols['location']:
                    observation, reward, done, _ = game.step((action, [block, location]))
                    child[(action, block, location)] = GologNode(game, self, done, observation, action, (block, location))  # Set args
        self.child = child

    def explore(self):
        current = self
        while current.child:
            child = current.child
            max_UCB = max(c.get_UCB_score() for c in child.values())
            actions = [action for action, node in child.items() if node.get_UCB_score() == max_UCB]
            if not actions:
                print("Error: zero length ", max_UCB)
            action = random.choice(actions)
            current = child[action]

        if current.N < 1:
            current.T = current.T + current.rollout()
        else:
            current.create_child()
            if current.child:
                current = random.choice(list(current.child.values()))
            current.T = current.T + current.rollout()

        current.N += 1

        parent = current
            
        while parent.parent:
            parent = parent.parent
            parent.N += 1
            parent.T = parent.T + current.T

    def rollout(self):
        if self.done:
            return 0
        
        v = 0
        done = False
        new_game = copy.deepcopy(self.game)
        while not done:
            action_index = new_game.action_space.sample()
            block = random.choice(new_game.state.symbols['block'])
            location = random.choice(new_game.state.symbols['location'])
            _, reward, done, _ = new_game.step((action_index, [block, location]))
            v += reward
            if done:
                new_game.reset()
                new_game.close()
                break
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
            print("Error: zero length ", max_N)

        max_child = random.choice(max_children)

        return max_child, max_child.action_index, max_child.args



MCTS_POLICY_EXPLORE = 200  # Number of MCTS iterations

def Policy_Player_MCTS(mytree):
    for _ in range(MCTS_POLICY_EXPLORE):
        mytree.explore()
    
    next_tree, next_action, next_args = mytree.next()

    next_tree.detach_parent()
    return next_tree, next_action, next_args

# Example usage
def main():
    # Initialize the environment and state as before
    initial_state = GologState()
    initial_state.add_symbol('block', ['a', 'b', 'c'])
    initial_state.add_symbol('location', ['a', 'b', 'c', 'table'])
    initial_state.add_fluent('loc(a)', ['a', 'b', 'c', 'table'], 'c')
    initial_state.add_fluent('loc(b)', ['a', 'b', 'c', 'table'], 'table')
    initial_state.add_fluent('loc(c)', ['a', 'b', 'c', 'table'], 'b')
    
    def stack_precondition(state, x, y):
        return x != y and x != 'table' and state.fluents[f'loc({x})'].value != y and not any(state.fluents[f'loc({z})'].value == x for z in state.symbols['block'])

    def stack_effect(state, x, y):
        state.fluents[f'loc({x})'].set_value(y)

    def blocksworld_goal(state):
        return state.fluents['loc(a)'].value == 'table' and state.fluents['loc(b)'].value == 'a' and state.fluents['loc(c)'].value == 'b'

    stack_action = GologAction('stack', stack_precondition, stack_effect, [initial_state.symbols['block'], initial_state.symbols['location']])
    initial_state.add_action(stack_action)
    
    reward_e = 0   
    game = GologEnvironment(initial_state, blocksworld_goal)
    observation = game.reset()
    done = False
    
    new_game = copy.deepcopy(game)
    mytree = GologNode(new_game, None, False, observation, 0)
    

    while not done:
        mytree, action_index, args = Policy_Player_MCTS(mytree)
        observation, reward, done, _ = game.step((action_index, args))
        reward_e += reward
        print(f"Executing action: {game.state.actions[action_index].name} with args {args}")
        game.render()

        if done:
            print('reward_e ' + str(reward_e))
            print("Game over!")
            break

if __name__ == "__main__":
    main()
