from state import *
from game import *
from agent import *
from mcts import *
from mcts_uncertainty import *
from look_ahead import *
import time
import numpy as np

# def game(state):
#     while not state.is_winner():
#         actions = state.get_actions()
#         a = random.choice(actions)
#         state.transition(a)

#     winner = state.get_winner()
#     print("\n" + winner.name + " wins the game!!!")
#     return winner

def main():
    num_players = 3
    iterations = 10
    results = [0 for i in range(num_players)]
    blockPrint()
    t_start = time.perf_counter()
    for i in range(iterations):
        state = State(num_players=num_players, agents={0:"mcts_uncertainty", 1:"random", 2:"random"})
        while not state.is_winner():
            state.transition_old()
        results[state.get_winner().id] += 1
    enablePrint()
    t_stop = time.perf_counter()
    t_elapsed = t_stop-t_start
    print(f"Time (s): {t_elapsed}")
    # print(f"Num sims per search: {np.mean(mcts_num_sims)}")
    # print(f"Num searches per game : {len(mcts_num_sims)/iterations}")

    for i in range(num_players):
        print((results[i]*100)/iterations)

if __name__ == "__main__":
    main()









# a1 = None
# a2 = None
# a3 = None
# state.stage = 0
# if state.actor == mcts_id:
#     mcts = MCTS(state, mcts_id)
#     mcts.search()
#     a1 = mcts.best_move()
#     # print(f"Action: {a1}")
    
#     state.action = a1
#     for p in state.players:
#         a2 = random.choice(state.get_action_challenges(p))
#         if a2:
#             state.is_challenge = True
#             state.challenge = a2
#             break
#     if not a2:
#         for p in state.players:
#             a2 = random.choice(state.get_counteractions(p))
#             if a2:
#                 state.is_counteraction = True
#                 state.counteraction = a2
#                 break
#     if state.is_counteraction:
#         for p in state.players:
#             a3 = random.choice(state.get_counteraction_challenges(p))
#             if a3:
#                 state.is_counteraction_challenge = True
#                 state.counteraction_challenge = a3
#                 break
# else:
#     a1 = random.choice(state.get_actions())
#     state.action = a1
#     state.stage = 1
#     for p in state.players:
#         if p.id == mcts_id:
#             mcts = MCTS(state, mcts_id)
#             mcts.search()
#             a2 = mcts.best_move()
#             state.print()
#             print(f"Challenge: {a2}")
#             print(mcts.num_rollouts)
#         elif not a2:
#             a2 = random.choice(state.get_action_challenges(p))
#         if a2:
#             state.is_challenge = True
#             state.challenge = a2
#             break
#     if not a2:
#         state.stage = 2
#         for p in state.players:
#             if p.id == mcts_id:
#                 mcts = MCTS(state, mcts_id)
#                 mcts.search()
#                 a2 = mcts.best_move()
#                 # print(f"Counteraction: {a2}")
#             elif not a2:
#                 a2 = random.choice(state.get_counteractions(p))
#             if a2:
#                 state.is_counteraction = True
#                 state.counteraction = a2
#                 break
#         if a2:
#             state.stage = 3
#             for p in state.players:
#                 if p.id == mcts_id:
#                     mcts = MCTS(state, mcts_id)
#                     mcts.search()
#                     a3 = mcts.best_move()
#                     # print(f"Counteraction challenge: {a3}")
#                 elif not a3:
#                     a3 = random.choice(state.get_counteraction_challenges(p))
#                 if a3:
#                     state.counteraction_challenge = a3
#                     state.is_counteraction_challenge = True
#                     break