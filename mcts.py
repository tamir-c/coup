import random
from copy import deepcopy
import numpy as np
from game import *

class Node:
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
        self.num_sims = 0
        self.num_wins = 0
        self.children = []
        # self.outcome = 
    
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
            return (self.num_wims / self.num_sims) + explore * np.sqrt(np.log(self.parent.num_sims) / self.num_sims)
        
class MCTS:
    def select_node(self):
        node = self.root
        state = deepcopy(self.root_state)

        while len(node.children) != 0:
            children = node.children
            max_value = 0
            for c in children:
                if c.value() > max_value:
                    max_value = c.value()
            max_nodes = [c for c in children if c.value() == max_value]

            node = random.choice(max_nodes)
            state.transition(node.action)

            if node.num_sims == 0:
                return node, state

        if self.expand(node, state):
            node = random.choice(node.children)
            state.transition(node.action)

        return node, state
    
    def expand(self, parent, state):
        if is_winner(state.players):
            return False
        
        children = [Node(action, parent)]