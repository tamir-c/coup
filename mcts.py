import random
from copy import deepcopy
import numpy as np
from game import *
import time
from state import *
from agent import *

# MCTS taught by and adapted from
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

    def uct(self, c = np.sqrt(2)):
        if self.num_sims == 0:
            if c == 0:
                return 0
            else:
                return float('inf')
        else:
            return (self.num_wins / self.num_sims) + c * np.sqrt(np.log(self.parent.num_sims) / self.num_sims)
        
class MCTS:
    def __init__(self, state, id = 0):
        self.id = id
        self.root_state = deepcopy(state)
        self.original_state = state
        self.root = Node(None, 0)

    def select_node(self):
        state = deepcopy(self.root_state)
        children = self.root.children
        max_val = children[0].uct()
        for c in children:
            if c.uct() > max_val:
                max_val = c.uct()
        max_nodes = [c for c in children if c.uct() == max_val]
        node = random.choice(max_nodes)
        action = state.get_all_actions(self.id)[node.index]
        state.random_transition(action)
        if node.num_sims == 0:
            return node, state
        return node, state
    
    def expand(self, parent, state): 
        if state.is_winner():
            return False
        if parent != self.root:
            return False
        actions = state.get_all_actions(self.id)
        children = [Node(parent, i) for i in range(len(actions))]
        parent.add_children(children)
        return True
    
    def roll_out(self, state):
        for i, p in enumerate(state.players):
            p.agent = RandomAgent(i)
        while not state.is_winner():
            state.transition(is_print=False) # plays game out until the end and returns winner.id
        return state.get_winner().id
    
    def back_propagate(self, node, outcome):
        if outcome == self.id: # If mcts won
            reward = 1
        else:
            reward = 0
        while node is not None: # Full back propogation does not need to be implemented because search depth is capped at 1
            node.num_sims += 1
            node.num_wins += reward
            node = node.parent
    
    # Selects nodes using uct formula and simulates transitions until the time limit is depleated
    def search(self, time_limit = 0.05):
        t_start = time.process_time()
        self.expand(self.root, self.root_state)
        n_rollouts = 0
        while time.process_time() - t_start < time_limit:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            self.back_propagate(node, outcome)
            n_rollouts += 1
        # Code used for recording how many roll outs are performed on average - commented out when not in use for performance reasons
        # mcts_num_sims.append(n_rollouts)
        # Note: len(mcts_num_sims) gives number of MCTS searches have been performed 

    # Due to the nature of the uct formula used for selection, the best node is that which is simulated the most,
    # not necessarily the node with the highest reward or reward to number of simulations ratio
    def best_move(self):
        if self.root_state.is_winner():
            raise Exception("Searching for terminal state!")
        
        max_val = self.root.children[0].num_sims
        for c in self.root.children:
            if c.num_sims > max_val:
                max_val = c.num_sims
        max_nodes = [c for c in self.root.children if c.num_sims == max_val]
        best_child = self.original_state.get_all_actions(self.id)[random.choice(max_nodes).index]
        return best_child
    
    def best_move_index(self): # returns index of the best action rather than the action itself
        if self.root_state.is_winner():
            raise Exception("Searching for a terminal state!")
        
        max_val = self.root.children[0].num_sims
        for c in self.root.children:
            if c.num_sims > max_val:
                max_val = c.num_sims
        max_nodes = [c for c in self.root.children if c.num_sims == max_val]
        return random.choice(max_nodes).index # The index in the list of actions available in a given state remains constant due to the deterministic nature of get_actions()
        

class MCTSAgent(BaseAgent):
    def __init__(self, id):
        self.id = id
        self.name = "MCTS Agent"

    def choice(self, state):
        if not state.players[self.id].check_player_in():
            return None
        mcts = MCTS(state, self.id)
        mcts.search()
        return mcts.best_move()