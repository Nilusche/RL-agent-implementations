import gym
import numpy as np
import matplotlib.pyplot as plt
import time
from gym.envs.registration import register
import os

register(id='FrozenLakeNotSlipppery-v0', entry_point='gym.envs.toy_text:FrozenLakeEnv',kwargs={'map_name': '4x4', 'is_slippery': False},max_episode_steps=100,reward_threshold=0.78)

env = gym.make('FrozenLakeNotSlipppery-v0')
env.reset()

'''
for step in range(5):
    env.render()
    action = env.action_space.sample()
    observation, reward, done, info = env.step(action)
    time.sleep(0.2)
    os.system('cls' if os.name == 'nt' else 'clear')
    if done:
        env.reset()

env.close()
'''

## Q Table
action_size = env.action_space.n
state_size = env.observation_space.n
# row states  columns actions
q_table = np.zeros([state_size, action_size])

## Hyperparameters
EPOCHS = 20000 # number of episodes
ALPHA = 0.8 # Learning rate
GAMMA = 0.95 # Discount factor
epsilon = 1.0 # Exploration rate
max_epsilon = 1.0 # Exploration probability at start
min_epsilon = 0.01 # Minimum exploration probability at end
decay_rate = 0.001 # Exponential decay rate for exploration probability

def epsilon_greedy_action_selection(epsilon, q_table, discrete_state):
    # EXPLORATION
    if np.random.rand() <= epsilon:
        return env.action_space.sample()
    # EXPLOITATION
    else:
        return np.argmax(q_table[discrete_state])

def compute_next_q_value(old_q_value, reward, new_q_value):
    return old_q_value + ALPHA * (reward + GAMMA * new_q_value - old_q_value)

def reduce_epsilon(epoch):
    return min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay_rate * epoch)


rewards = []
log_interval = 100

for epoch in range(EPOCHS):
    discrete_state = env.reset()
    done = False
    total_reward = 0
    
    while not done:
        # ACTION
        action = epsilon_greedy_action_selection(epsilon, q_table, discrete_state)
        # state, reward .. env.step()
        new_discrete_state, reward, done, info = env.step(action)
        # Old (Current) Q Value
        old_q_value = q_table[discrete_state, action]
        # New (Next) Q Value
        new_q_value = np.max(q_table[new_discrete_state])
        # Compute Next Q Value
        next_q_value = compute_next_q_value(old_q_value, reward, new_q_value)
        # Update Q Table
        q_table[discrete_state, action] = next_q_value
        # track rewards
        total_reward += reward
        # update state
        discrete_state = new_discrete_state

    # Exploration rate decay
    epsilon = reduce_epsilon(epoch)
    rewards.append(total_reward)
    
    if epoch % log_interval == 0:
        print('Sum of rewards: {}'.format(np.sum(rewards)))
env.close()

state = env.reset()

for steps in range(100):
    env.render()
    action = np.argmax(q_table[state])
    state, reward, done, info = env.step(action)
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    if done:
        print('Finished in {} steps'.format(steps))
        env.reset()
        break
env.close()