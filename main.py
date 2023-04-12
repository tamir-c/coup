import random
from game import *
import time
import copy
import sys, os
from agent import *
from mcts import *

# Functions to block and enable calls to print (used to speed up testing agents)
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
def enablePrint():
    sys.stdout = sys.__stdout__

def game(state):
    blockPrint()
    while not state.is_winner():
        actions = state.get_actions()
        a = random.choice(actions)
        state.transition(a)

    winner = state.get_winner()
    print("\n" + winner.name + " wins the game!!!")
    enablePrint()
    return winner

def main():
    blockPrint()
    iterations = 1
    num_players=3
    results = [0 for i in range(num_players)]
    for i in range(iterations):
        s = State(num_players=num_players, 
                  agents={},
                #   agents={0:RandomNoBluffAgent(), 7:RandomNoChallengeAgent(), 7:RandomNoChallengeAgent()}
                  )
        mcts = MCTS(s)
        mcts.search()
        a = mcts.best_move()
        enablePrint()
        print(a)
        print(f"MCTS ran for {mcts.run_time} seconds, generating {mcts.node_count} nodes with {mcts.num_rollouts} rollouts.")
    #     result = game(s)
    #     results[result.id] += 1
    # for i in range(num_players):
    #     print((results[i]*100)/iterations)


    #else: # resume already existing game from state string - not a priority
    #   pass
        # string = "2-6-0-0-1-0-9-4-1-3-0-1-0-0-0-0-2"


if __name__ == "__main__":
    main()