from copy import deepcopy
from mcts import *
from state import *
from statistics import multimode
import sys, os
        
class MCTSUncertainty:
    def __init__(self, state, id):
        if not (state.num_players == 2 or state.num_players == 3):
            raise Exception("This agent only works for 3 player Coup")
        self.id = id
        self.root_state = deepcopy(state)
        self.original_state = state

    def search(self, time_limit = 0.05):
        # redeal opponents influences
        best_actions = []
        state = deepcopy(self.root_state)
        if state.num_players == 2:
            ops = [0,1]
            ops.remove(self.id)
            op1 = state.players[int(ops[0])]
            for i in range(5):
                op1.redeal_opponents(i)
                mcts = MCTS(state, self.id)
                mcts.search()
                best_actions.append(mcts.best_move_index())
        elif state.num_players == 3:
            ops = [0,1,2]
            ops.remove(self.id)
            op1 = state.players[int(ops[0])]
            op2 = state.players[int(ops[1])]
            for i in range(5):
                op1.redeal_opponents(i)
                for j in range(5):
                    op2.redeal_opponents(j)
                    mcts = MCTS(state, self.id)
                    mcts.search()
                    best_actions.append(mcts.best_move_index())
        index = random.choice(multimode(best_actions))
        return self.original_state.get_all_actions(self.id)[index]

        # call MCTS search and get best action
        # save best action
        # return modal action

class MCTSUncertaintyAgent(BaseAgent):
    def __init__(self, id):
        self.id = id
        self.name = "MCTS Unceratinty Agent"

    def choice(self, state, msg=""):
        printing = isPrinting()
        blockPrint()
        if not state.players[self.id].check_player_in():
            return None
        mcts = MCTSUncertainty(state, self.id)
        ret = mcts.search()
        if printing: enablePrint()
        return ret
    
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
def enablePrint():
    sys.stdout = sys.__stdout__
def isPrinting():
    if sys.stdout == sys.__stdout__:
        return True
    return False