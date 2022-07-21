from venv import create
import gym
import numpy as np
import matplotlib.pyplot as plt
import time
from gym.envs.registration import register
import os

env = gym.make("MountainCar-v0")
env.reset()

"""
for step in range(100):
    env.render();
    action = env.action_space.sample()
    observation, reward, done, infor = env.step(action)
    print(reward)
    time.sleep(0.02)
env.close();
"""

def create_bins(num_bins_per_action = 10):
    bins_car_position = np.linspace(-1.2, 0.6, num_bins_per_action)
    bins_car_velocity = np.linspace(-0.07, 0.07, num_bins_per_action)
    return np.array([bins_car_position, bins_car_velocity])

NUM_BINS = 40 
BINS = create_bins(NUM_BINS)

def discretize_observation(observations, bins):
    binned_observations = []
    for i , observation in enumerate(observations):
        binned_observations.append(np.digitize(observation, bins[i]))
    return tuple(binned_observations)

q_table_shape  = (NUM_BINS, NUM_BINS, env.action_space.n)
q_table = np.zeros(q_table_shape)


def epsilon_greedy_action_selection(epsilon, q_table, discrete_state):
    # EXPLORATION
    if np.random.rand() <= epsilon:
        return env.action_space.sample()
    # EXPLOITATION
    else:
        return np.argmax(q_table[discrete_state])

EPOCHS = 15000 # number of episodes
ALPHA = 0.8 # Learning rate
GAMMA = 0.9 # Discount factor
epsilon = 1.0 # Exploration rate
BURN_IN = 100
EPSILON_END =10000
EPSILON_REDUCE = 0.0001


def compute_next_q_value(old_q_value, reward, new_q_value):
    return old_q_value + ALPHA * (reward + GAMMA * new_q_value - old_q_value)


def reduce_epsilon(epsilon, epoch):
    if BURN_IN <= epoch < EPSILON_END:
        epsilon -= EPSILON_REDUCE
    return epsilon


def fail(done, points, reward):
    if done and points < -150:
        reward = 200
    return reward


rewards = []
log_interval = 500

#Plot analysis
fig = plt.figure()
ax = fig.add_subplot(111)
plt.ion()
fig.canvas.draw()
plt.show()

max_position_log = []
mean_position_log = []
epochs = []

"""
for epoch in range(EPOCHS):
    initial_state = env.reset()
    discrete_state = discretize_observation(initial_state, BINS)
    done = False
    points = 0

    max_position = -np.inf
    epochs.append(epoch)

    while not done:
        action = epsilon_greedy_action_selection(epsilon, q_table, discrete_state)
        next_state, reward, done, infor = env.step(action)

        position, velocity = next_state 

        reward = fail(done, points, reward)

        next_discrete_state = discretize_observation(next_state, BINS)

        old_q_value = q_table[discrete_state + (action,)]
        next_optimal_q_value = np.max(q_table[next_discrete_state])

        new_q_value = compute_next_q_value(old_q_value, reward, next_optimal_q_value)
        q_table[discrete_state + (action,)] = new_q_value
        
        if position > max_position:
            max_position = position
        discrete_state = next_discrete_state
        points += 1
    
    epsilon = reduce_epsilon(epsilon,epoch)

    max_position_log.append(max_position)
    running_mean = round(np.mean(max_position_log[-30:]), 2)
    mean_position_log.append(running_mean)
    print(epoch, "....", points)

    if epoch % log_interval == 0:
        ax.clear()
        ax.scatter(epochs, max_position_log)
        ax.plot(epochs, max_position_log)
        ax.plot(epochs, mean_position_log, label='Running Mean')
        plt.legend()
        fig.canvas.draw()
        plt.pause(0.01) 

env.close()


with open('q_table_mountaincar.txt', 'wb') as f:
    np.save(f, q_table)
"""



with open('q_table_mountaincar.txt', 'rb') as f:
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




