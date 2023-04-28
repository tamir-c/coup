import random
from copy import deepcopy
import numpy as np
from game import *
import time
from state import *
from agent import *

# Significant portions of code found from
# https://www.harrycodes.com/blog/monte-carlo-tree-search

mcts_num_sims = [] # number of simulations per 

class Node:
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index
        self.num_sims = 0
        self.num_wins = 0
        self.children = []
    
    def add_children(self, children):
        for c in children:
            self.children.append(c)

    def value(self, explore = np.sqrt(2)):
        if self.num_sims == 0:
            if explore == 0:
                return 0
            else:
                return float('inf')
        else:
            return (self.num_wins / self.num_sims) + explore * np.sqrt(np.log(self.parent.num_sims) / self.num_sims)
        
class MCTS:
    def __init__(self, state, id = 0):
        self.id = id
        self.root_state = deepcopy(state)
        self.original_state = state
        self.root = Node(None, 0)
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0

    def select_node(self):
        state = deepcopy(self.root_state)
        children = self.root.children
        max_value = children[0].value()
        for c in children:
            if c.value() > max_value:
                max_value = c.value()
        max_nodes = [c for c in children if c.value() == max_value]
        node = random.choice(max_nodes)
        action = self.get_actions(state)[node.index]
        state.random_transition(action)
        if node.num_sims == 0:
            return node, state
        return node, state
    
    def expand(self, parent, state): 
        if state.is_winner():
            return False
        if parent != self.root:
            return False
        actions = self.get_actions(state)
        children = [Node(parent, i) for i in range(len(actions))]
        parent.add_children(children)
        return True
    
    def get_actions(self, state):
        if state.stage == 0:
            actions = state.get_actions()
        elif state.stage == 1:
            actions = state.get_action_challenges(state.players[self.id])
        elif state.stage == 2:
            actions = state.get_counteractions(state.players[self.id])
        elif state.stage == 3:
            actions = state.get_counteraction_challenges(state.players[self.id])
        return actions
    
    def roll_out(self, state):
        for i, p in enumerate(state.players):
            p.agent = RandomAgent(i)
        while not state.is_winner():
            state.transition_old() # plays game out until the end and returns winner.id
        return state.get_winner().id
    
    def back_propagate(self, node, outcome): # turn is WRONG! NEEDS TO BE FIXED
        if outcome == self.id: # if mcts won
            reward = 1
        else:
            reward = 0
        while node is not None:
            node.num_sims += 1
            node.num_wins += reward
            node = node.parent
  

    def search(self, time_limit = 0.05):
        t_start = time.process_time()
        self.expand(self.root, self.root_state)
        n_rollouts = 0
        while time.process_time() - t_start < time_limit:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            self.back_propagate(node, outcome)
            n_rollouts += 1
        global mcts_num_sims
        mcts_num_sims.append(n_rollouts)

    def best_move(self):
        if self.root_state.is_winner():
            return -1
        
        max_value = self.root.children[0].num_sims
        for c in self.root.children:
            if c.num_sims > max_value:
                max_value = c.num_sims
        max_nodes = [c for c in self.root.children if c.num_sims == max_value]
        best_child = self.get_actions(self.original_state)[random.choice(max_nodes).index]
        return best_child

class MCTSAgent(object):
    def __init__(self, id):
        self.id = id
        self.name = "MCTS Agent"

    def choice(self, state, msg=""):
        if not state.players[self.id].check_player_in():
            return None
        mcts = MCTS(state, self.id)
        mcts.search()
        return mcts.best_move()