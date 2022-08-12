import gym
import numpy as np
from IPython import display
import matplotlib.pyplot as plt
from envs import Maze


env=Maze()

state = env.reset()
episode = []
done = False
while not done:
    action = env.action_space.sample()
    state, reward, done, info = env.step(action)
    episode.append((state, action, reward))
    env.render()
env.close()

print(episode)