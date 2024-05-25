# gologpacman.py
import pygame
from gologenv import *
from itertools import product
import time

# Define the Pac-Man environment
initial_state = GologState()
initial_state.add_symbol('entity', ['pacman', 'ghost1', 'ghost2'])
initial_state.add_symbol('location', [(x, y) for x in range(5) for y in range(5)])
initial_state.add_symbol('dot', [(x, y) for x in range(5) for y in range(5)])
initial_state.add_symbol('capsule', [(x, y) for x in range(5) for y in range(5)])

initial_state.add_fluent('loc(pacman)', initial_state.symbols['location'], (0, 0))
initial_state.add_fluent('loc(ghost1)', initial_state.symbols['location'], (4, 4))
initial_state.add_fluent('loc(ghost2)', initial_state.symbols['location'], (4, 3))

for dot in initial_state.symbols['dot']:
    initial_state.add_fluent(f'dot_present({dot})', [True, False], dot in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])

for capsule in initial_state.symbols['capsule']:
    initial_state.add_fluent(f'capsule_present({capsule})', [True, False], capsule in [(1, 1), (3, 3)])

initial_state.add_fluent('pacman_powered_up()', [True, False], False)
initial_state.add_fluent('power_up_timer()', list(range(11)), 0)

# Helper function to check adjacency
def adjacent(from_loc, to_loc):
    fx, fy = from_loc
    tx, ty = to_loc
    return abs(fx - tx) + abs(fy - ty) == 1

# Define actions
def move_precondition(state, x, from_loc, to_loc):
    return state.fluents[f'loc({x})'].value == from_loc and adjacent(from_loc, to_loc)

def move_effect(state, x, from_loc, to_loc):
    state.fluents[f'loc({x})'].set_value(to_loc)
    if state.fluents['pacman_powered_up()'].value:
        state.fluents['power_up_timer()'].set_value(state.fluents['power_up_timer()'].value - 1)
        if state.fluents['power_up_timer()'].value == 0:
            state.fluents['pacman_powered_up()'].set_value(False)

def eat_dot_precondition(state, x, d):
    return state.fluents[f'loc({x})'].value == d and state.fluents[f'dot_present({d})'].value

def eat_dot_effect(state, x, d):
    state.fluents[f'dot_present({d})'].set_value(False)

def eat_capsule_precondition(state, x, c):
    return state.fluents[f'loc({x})'].value == c and state.fluents[f'capsule_present({c})'].value

def eat_capsule_effect(state, x, c):
    state.fluents[f'capsule_present({c})'].set_value(False)
    state.fluents['pacman_powered_up()'].set_value(True)
    state.fluents['power_up_timer()'].set_value(10)

def eat_ghost_precondition(state, x, g):
    return state.fluents['pacman_powered_up()'].value and state.fluents[f'loc({x})'].value == state.fluents[f'loc({g})'].value

def eat_ghost_effect(state, x, g):
    state.fluents[f'loc({g})'].set_value((4, 4))

# Add actions to the environment
initial_state.add_action(GologAction('move', move_precondition, move_effect, ['entity', 'location', 'location']))
initial_state.add_action(GologAction('eat_dot', eat_dot_precondition, eat_dot_effect, ['pacman', 'dot']))
initial_state.add_action(GologAction('eat_capsule', eat_capsule_precondition, eat_capsule_effect, ['pacman', 'capsule']))
initial_state.add_action(GologAction('eat_ghost', eat_ghost_precondition, eat_ghost_effect, ['pacman', 'ghost']))

# Define goal
def pacman_goal(state):
    return all(not state.fluents[f'dot_present({d})'].value for d in initial_state.symbols['dot'])

# Define reward function
def pacman_reward(state):
    if pacman_goal(state):
        return 100
    if state.fluents['pacman_powered_up()'].value:
        return 5
    for d in initial_state.symbols['dot']:
        if state.fluents[f'dot_present({d})'].value and state.fluents[f'loc(pacman)'].value == d:
            return 10
    for c in initial_state.symbols['capsule']:
        if state.fluents[f'capsule_present({c})'].value and state.fluents[f'loc(pacman)'].value == c:
            return 20
    for g in ['ghost1', 'ghost2']:
        if state.fluents['pacman_powered_up()'].value and state.fluents[f'loc(pacman)'].value == state.fluents[f'loc({g})'].value:
            return 50
    return -1

# Create environment
env = GologEnvironment(initial_state, pacman_goal, initial_state.actions, pacman_reward)

# Define the play procedure
def play():
    env.reset()
    sequence = [
        ('move', ['pacman', (0, 0), (0, 1)]),
        ('eat_dot', ['pacman', (0, 1)]),
        ('move', ['pacman', (0, 1), (1, 1)]),
        ('eat_capsule', ['pacman', (1, 1)])
        # Add more moves and actions
    ]
    env.render()
    for action_name, args in sequence:
        action_index = next(i for i, a in enumerate(env.state.actions) if a.name == action_name)
        env.step((action_index, args))
        env.render()

    #kleep the window open
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return



# Define the rendering function using Pygame
def render():
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Pac-Man")
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)

    # Grid dimensions
    grid_size = 100
    margin = 5


    screen.fill(BLACK)

    # Draw the grid
    for row in range(5):
        for col in range(5):
            color = WHITE
            pygame.draw.rect(screen,
                                color,
                                [(margin + grid_size) * col + margin,
                                (margin + grid_size) * row + margin,
                                grid_size,
                                grid_size])

    # Draw dots
    for dot in initial_state.symbols['dot']:
        if env.state.fluents[f'dot_present({dot})'].value:
            pygame.draw.circle(screen,
                                BLUE,
                                [(margin + grid_size) * dot[0] + margin + grid_size // 2,
                                (margin + grid_size) * dot[1] + margin + grid_size // 2],
                                10)

    # Draw capsules
    for capsule in initial_state.symbols['capsule']:
        if env.state.fluents[f'capsule_present({capsule})'].value:
            pygame.draw.circle(screen,
                                GREEN,
                                [(margin + grid_size) * capsule[0] + margin + grid_size // 2,
                                (margin + grid_size) * capsule[1] + margin + grid_size // 2],
                                15)

    # Draw ghosts
    ghost1_loc = env.state.fluents['loc(ghost1)'].value
    ghost2_loc = env.state.fluents['loc(ghost2)'].value
    pygame.draw.circle(screen,
                        RED,
                        [(margin + grid_size) * ghost1_loc[0] + margin + grid_size // 2,
                        (margin + grid_size) * ghost1_loc[1] + margin + grid_size // 2],
                        20)
    pygame.draw.circle(screen,
                        RED,
                        [(margin + grid_size) * ghost2_loc[0] + margin + grid_size // 2,
                        (margin + grid_size) * ghost2_loc[1] + margin + grid_size // 2],
                        20)

    # Draw Pac-Man
    pacman_loc = env.state.fluents['loc(pacman)'].value
    pygame.draw.circle(screen,
                        YELLOW,
                        [(margin + grid_size) * pacman_loc[0] + margin + grid_size // 2,
                        (margin + grid_size) * pacman_loc[1] + margin + grid_size // 2],
                        25)

    #pygame.display.flip()
    

    
    pygame.display.update()
    time.sleep(0.5)



# Attach the render function to the environment
env.render = render

# Execute the play procedure
if __name__ == "__main__":
    play()
