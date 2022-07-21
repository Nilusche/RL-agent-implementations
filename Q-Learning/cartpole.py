from venv import create
import gym
import numpy as np
import matplotlib.pyplot as plt
import time
from gym.envs.registration import register
import os

env = gym.make('CartPole-v0')
env.reset()




for step in range(100):
    #env.render();
    action = env.action_space.sample()
    observation, reward, done, infor = env.step(action)
    #print(observation)
    #time.sleep(0.02)

env.close();

def create_bins(num_bins_per_action = 10):
    bins_cart_position = np.linspace(-4.8, 4.8, num_bins_per_action)
    bins_cart_velocity = np.linspace(-5, 5, num_bins_per_action)
    bins_pole_angle = np.linspace(-0.418, 0.418, num_bins_per_action)
    bins_pole_velocity = np.linspace(-5, 5, num_bins_per_action)
    bins = np.array([bins_cart_position, bins_cart_velocity, bins_pole_angle, bins_pole_velocity])
    return bins

NUM_BINS = 10
BINS = create_bins(NUM_BINS)

def discretize_observation(observations, bins):
    binned_observations = []
    for i , observation in enumerate(observations):
        binned_observations.append(np.digitize(observation, bins[i]))
    
    return tuple(binned_observations)

#observations = env.reset()
#binned_observations = discretize_observation(observations, BINS)
#print(binned_observations)

q_table_shape  = (NUM_BINS, NUM_BINS, NUM_BINS, NUM_BINS, env.action_space.n)
q_table = np.zeros(q_table_shape)



def epsilon_greedy_action_selection(epsilon, q_table, discrete_state):
    # EXPLORATION
    if np.random.rand() <= epsilon:
        return env.action_space.sample()
    # EXPLOITATION
    else:
        return np.argmax(q_table[discrete_state])

EPOCHS = 20000 # number of episodes
ALPHA = 0.8 # Learning rate
GAMMA = 0.9 # Discount factor

def compute_next_q_value(old_q_value, reward, new_q_value):
    return old_q_value + ALPHA * (reward + GAMMA * new_q_value - old_q_value)

epsilon = 1
BURN_IN = 1
EPSILON_END =10000
EPSILON_REDUCE = 0.0001

def reduce_epsilon(epsilon, epoch):
    if BURN_IN <= epoch < EPSILON_END:
        return epsilon - EPSILON_REDUCE
    return epsilon

def fail(done, points, reward):
    if done and points < 150:
        reward = -200
    return reward

epsilon =1.0
rewards = []
log_interval = 500
render_interval = 10000
"""
fig = plt.figure()
ax = fig.add_subplot(111)
plt.ion()
fig.canvas.draw()
plt.show()
"""


"""
points_log = []
mean_points_log = []
epochs = []

for epoch in range(EPOCHS):
    initial_state = env.reset()
    discrete_state = discretize_observation(initial_state, BINS)
    done = False
    points = 0

    epochs.append(epoch)
    while not done:
        action = epsilon_greedy_action_selection(epsilon, q_table, discrete_state)
        next_state, reward, done, info = env.step(action)

        reward = fail(done, points, reward)

        next_state_discrete = discretize_observation(next_state, BINS)

        old_q_value = q_table[discrete_state + (action,)]
        next_optimal_q_value = np.max(q_table[next_state_discrete])

        next_q_value = compute_next_q_value(old_q_value, reward, next_optimal_q_value)
        q_table[discrete_state + (action,)] = next_q_value

        discrete_state = next_state_discrete
        points += 1

    epsilon = reduce_epsilon(epsilon, epoch)
    points_log.append(points)
    running_mean = round(np.mean(points_log[-30:]), 2)
    mean_points_log.append(running_mean)
    print(epoch)

    if epoch % log_interval == 0:
        
        '''
        ax.clear()
        ax.scatter(epochs, points_log)
        ax.plot(epochs, points_log)
        ax.plot(epochs, mean_points_log, label='Running Mean')
        plt.legend()
        fig.canvas.draw()
        plt.pause(0.01) 
        '''

env.close()

with open('q_table_cartpole.txt', 'wb') as f:
    np.save(f, q_table)
"""



with open('q_table_cartpole.txt', 'rb') as f:
    q_table = np.load(f)
observation = env.reset()
rewards = 0
for step in range(1000):
    env.render()
    discrete_state = discretize_observation(observation, BINS)
    action = np.argmax(q_table[discrete_state])
    observation, reward, done, info = env.step(action)
    rewards += 1

    if done: 
        print("Finished with score of ", rewards)
        break
