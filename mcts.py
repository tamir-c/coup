import random
from copy import deepcopy
import numpy as np
from game import *
import time

class Node:
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
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
    def __init__(self, state):
        self.id = 0
        self.root_state = deepcopy(state)
        self.root = Node(None, None)
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0

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
        if state.is_winner():
            return False
        
        actions = state.get_actions()
        children = [Node(action, parent) for action in actions]
        parent.add_children(children)

        return True
    
    def roll_out(self, state):
        while not state.is_winner():
            actions = state.get_actions()
            a = random.choice(actions)
            state.transition(a)
        return state.get_winner().id
    
    def back_propagate(self, node, turn, outcome):
        if outcome == self.id:
            reward = 1
        else:
            reward = 0
        
        while node is not None:
            node.num_sims += 1
            node.num_wins += reward
            node = node.parent
            if turn == self.id:
                reward = 1
            else:
                reward = 0

    def search(self, time_limit = 2):
        t_start = time.process_time()

        n_rollouts = 0
        while time.process_time() - t_start < time_limit:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            self.back_propagate(node, state.actor, outcome)
            n_rollouts += 1

        run_time = time.process_time() - t_start
        self.run_time = run_time
        self.num_rollouts = n_rollouts

    def best_move(self):
        if self.root_state.is_winner():
            return -1
        
        max_value = 0
        for c in self.root.children:
            if c.num_sims > max_value:
                max_value = c.num_sims
        max_nodes = [c for c in self.root.children if c.num_sims == max_value]
        best_child = random.choice(max_nodes)
        return best_child.action