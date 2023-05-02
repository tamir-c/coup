from state import *
from game import *
from agent import *
from mcts import *
from mcts_uncertainty import *
from look_ahead import *
import time

# Manually test different agents against each other over many games to assess which strategies win in the long run
# INSTRUCTIONS
# Only modify the code between the two dotted-line comments
# Set num_players 2<=num_players<=6
# Set the number of iterations (games) you wish to execute
# Modify the agents dictionary to choose which agent you wish the player at index key to implement

def main():
    # ----------------------------------------------------------------
    num_players = 3
    iterations = 100 # Dictates how many games are played
    agents = {0:"mcts", 1:"random_no_challenge", 2:"random_no_challenge"} # Dictates the strategy of player with index of key in state.players
    # -----------------------------------------------------------------

    results = [0 for i in range(num_players)]
    t_start = time.perf_counter()

    for i in range(iterations):
        state = State(num_players=num_players, agents=agents)
        while not state.is_winner():
            state.transition(is_print=False)
        results[state.get_winner().id] += 1

    t_stop = time.perf_counter()
    t_elapsed = t_stop-t_start
    print(f"Time elapsed (s): {t_elapsed}")

    # Used for gathering data about mcts
    # print(f"Num sims per search: {np.mean(mcts_num_sims)}")
    # print(f"Num searches per game : {len(mcts_num_sims)/iterations}")

    for i, p in enumerate(state.players):
        print(f"{p} - {p.agent.name} won {(results[i]*100)/iterations}% of {iterations} games.")


    # print(f"Num bluffs = {bluffs}.")
    # print(f"Num bluffable = {bluffable}.")

if __name__ == "__main__":
    main()