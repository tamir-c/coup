from copy import deepcopy
from mcts import *
from state import *
from statistics import multimode

bluffs = []
bluffable = []

class MCTSUncertainty:
    def __init__(self, state, id):
        if not (state.num_players == 2 or state.num_players == 3):
            raise Exception("This agent only works for 3 player Coup")
        self.id = id
        self.root_state = deepcopy(state)
        self.original_state = state # Used to return the chosen action. Returning an action belonging to a deepcopy of the original state as this would not work

    # Searches for the best mcts action for a state for each possible card type between players,
    # as an approximation to searching for every possible combination of two cards.
    # Returns modal action, i.e. action that is most robust to the uncertainty of not knowing opponents influences
    # Only implemented for 2 and 3 players only due to exponential search time
    def search(self):
        # redeal opponents influences
        # call MCTS search and get best action
        # save best action
        # return modal action
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
        d = self.original_state.get_all_actions(self.id)[index]
        # self.updateData(d)
        return d
    
    def updateData(self, decision):
        global num_bluffs
        global num_bluffable
        if decision == None:
            return
        a, b = decision.is_bluff()
        if a == None or b == None:
            return
        if a: bluffs.append(a)
        if b: bluffable.append(b)

class MCTSUncertaintyAgent(BaseAgent):
    def __init__(self, id):
        self.id = id
        self.name = "MCTS Unceratinty Agent"

    def choice(self, state):
        if not state.players[self.id].check_player_in():
            return None
        mcts_uncertainty = MCTSUncertainty(state, self.id)
        return mcts_uncertainty.search()