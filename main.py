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
    iterations = 1
    num_players=3
    results = [0 for i in range(num_players)]
    for i in range(iterations):
        state = State(num_players=num_players, 
                  agents={},
                #   agents={0:RandomNoBluffAgent(), 7:RandomNoChallengeAgent(), 7:RandomNoChallengeAgent()}
                  )
        
        while not state.is_winner():
            a1 = None
            a2 = None
            a3 = None
            state.stage = 0
            if state.actor == 0:
                mcts = MCTS(state)
                mcts.search()
                a1 = mcts.best_move()
                state.action = a1
                for p in state.players:
                    a2 = random.choice(get_action_challenges(a1, p))
                    if a2:
                        state.is_challenge = True
                        state.challenge = a2
                        break
                if not a2:
                    for p in state.players:
                        a2 = random.choice(state.get_counteractions(p))
                        if a2:
                            state.is_counteraction = True
                            state.counteraction = a2
                            break
                if state.is_counteraction:
                    for p in state.players:
                        a3 = get_counteraction_challenges(a2, p)
                        if a3:
                            state.is_counteraction_challenge = True
                            state.counteraction_challenge = a3

            else:
                a1 = random.choice(state.get_actions())
                state.action = a1
                state.stage = 1
                for p in state.players:
                    if p.id == 0:
                        mcts = MCTS(state)
                        mcts.search()
                        a2 = mcts.best_move()
                    elif not a2:
                        a2 = random.choice(get_action_challenges(a1, p))
                    if a2:
                        state.is_challenge = True
                        state.challenge = a2
                        break
                if not a2:
                    state.stage = 2
                    for p in state.players:
                        if p.id == 0:
                            mcts = MCTS(state)
                            mcts.search()
                            a2 = mcts.best_move()
                        elif not a2:
                            a2 = random.choice(state.get_counteractions(p))
                        if a2:
                            state.is_counteraction = True
                            state.counteraction = a2
                            break
                    if a2:
                        state.stage = 3
                        for p in state.players:
                            if p.id == 0:
                                mcts = MCTS(state)
                                mcts.search()
                                a3 = mcts.best_move()
                            elif not a3:
                                a3 = random.choice(get_counteraction_challenges(a2, p))
                            if a3:
                                state.counteraction_challenge = a3
                                state.is_counteraction_challenge = True
                
            state.transition(a1, a2, a3)
    
        winner = state.get_winner()
        results[winner.id] += 1
    for i in range(num_players):
        print((results[i]*100)/iterations)

    # print(f"MCTS ran for {mcts.run_time} seconds, generating {mcts.node_count} nodes with {mcts.num_rollouts} rollouts.")

    #else: # resume already existing game from state string - not a priority
    #   pass
        # string = "2-6-0-0-1-0-9-4-1-3-0-1-0-0-0-0-2"


if __name__ == "__main__":
    main()