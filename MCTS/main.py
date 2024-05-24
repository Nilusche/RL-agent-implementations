import sys
from parser import parser

def main(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    env = parser.parse(content).get_environment()
    return env

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python parser.py <path_to_gpp_file>")
    # else:
    #     env = main(sys.argv[1])

    env = main("blocksworld.gpp")

    
    # You can now use the env object as needed, e.g., running MCTS on it
    # For example:
    from gologmcts import Policy_Player_MCTS, GologNode
    import copy

    observation = env.reset()
    done = False
    new_game = copy.deepcopy(env)
    mytree = GologNode(new_game, None, False, observation, 0)

    step_counter = 0
    while not done:
        mytree, action_index, args = Policy_Player_MCTS(mytree)
        observation, reward, done, _ = env.step((action_index, args))
        print(f"Step {step_counter}: Executing action: {env.state.actions[action_index].name} with args {args}")
        env.render()

        if done:
            print("Game over!")
            break

        step_counter += 1
