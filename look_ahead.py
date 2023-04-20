
import random
from copy import deepcopy
from game import *
import time
from state import *
from agent import *

class Node:
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
        self.num_sims = 0
        self.reward = 0
        self.children = []
    
    def add_children(self, children):
        for c in children:
            self.children.append(c)

class LookAhead():
    def __init__(self, state, id):
        self.id = id
        self.root_state = deepcopy(state)
        self.root = Node(None, None)

    def expand(self, parent, state): 
        if state.is_winner():
            return False
        if parent != self.root:
            return False
        if state.stage == 0:
            actions = state.get_actions()
        elif state.stage == 1:
            actions = state.get_action_challenges(state.players[self.id])
        elif state.stage == 2:
            actions = state.get_counteractions(state.players[self.id])
        elif state.stage == 3:
            actions = state.get_counteraction_challenges(state.players[self.id])
        children = [Node(action, parent) for action in actions]
        parent.add_children(children)
        self.node_count += len(children)
        return True

    def get_reward(self, state):
        reward = 0
        influences = state.players[self.id].num_influences()
        if 
        reward += state.players[self.id].coins * 10
        reward += state.players[self.id].get * 10

    
    def search(self, time_limit):
        self.expand(self.root, self.root_state)
        t_start = time.process_time()
        while time.process_time() - t_start < time_limit:
            for child in self.root.children:
                state = deepcopy(self.root_state)
                state.random_transition(child, state)
                reward = self.get_reward(state)
                child.reward += reward
                child.num_sims += 1


class LookAheadAgent():
    def __init__(self, id):
        self.id = id
        self.name = "One Step Look Ahead Agent"
    def choice(state):

    
