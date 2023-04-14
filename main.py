import random
from game import *
import time
import copy
from agent import *
from mcts import *
from state import *


def game(state):
    while not state.is_winner():
        actions = state.get_actions()
        a = random.choice(actions)
        state.transition(a)

    winner = state.get_winner()
    print("\n" + winner.name + " wins the game!!!")
    return winner

def main():
    iterations = 1000
    num_players=3
    results = [0 for i in range(num_players)]
    for i in range(iterations):
        state = State(num_players=num_players, agents={})
        
        winner_id = state.random_sim()

        results[winner_id] += 1
    for i in range(num_players):
        print((results[i]*100)/iterations)

if __name__ == "__main__":
    main()
