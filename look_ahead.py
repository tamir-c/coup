import random
from copy import deepcopy
from game import *
import time
from agent import *
import sys, os

la_num_sims = []

class NodeState:
    def __init__(self, state, actions):
        self.state = state
        self.actions = actions

class Node:
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index
        self.num_sims = 0
        self.reward = 0
        self.children = []
    
    def add_children(self, children):
        for c in children:
            self.children.append(c)

class LookAhead:
    def __init__(self, state, id):
        self.id = id
        self.root_state = deepcopy(state)
        self.root = Node(None, 0)
        self.original_state = state
        self.run_time = 0

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

    def expand(self):
        state = deepcopy(self.root_state) 
        actions = self.get_actions(state)
        children = [Node(self.root, i) for i in range(len(actions))]
        self.root.add_children(children)
    
    def search(self, time_limit=0.05):
        state = self.expand()
        i = 0
        t_start = time.process_time()
        state = deepcopy(self.root_state)
        actions = self.get_actions(state)
        master = NodeState(state, actions)
        while time.process_time() - t_start < time_limit:
            ns = deepcopy(master)
            state = ns.state
            action = ns.actions[i]
            child = self.root.children[i]
            state.random_transition(action)
            reward = self.get_reward(state)
            child.reward += reward
            child.num_sims += 1
            self.root.num_sims +=1
            i += 1
            if i % len(self.root.children) == 0:
                i = 0
        self.run_time = time.process_time() - t_start
        
        global la_num_sims
        la_num_sims.append(self.root.num_sims)


    def best_move(self):
        if self.root_state.is_winner():
            return -1
        max_value = self.root.children[0].reward / self.root.children[0].num_sims
        for c in self.root.children:
            if c.reward/c.num_sims > max_value:
                max_value = c.reward / c.num_sims
        max_nodes = [c for c in self.root.children if c.reward/c.num_sims == max_value]
        best_child = random.choice(max_nodes)
        return self.get_actions(self.original_state)[best_child.index]
    
    def get_reward(self, state):
        reward = 0
        root_inf = {}
        lose_inf = 0

        for i, p in enumerate(self.root_state.players):
            root_inf[i] = p.num_influences()
        for i, p in enumerate(state.players):
            if p.num_influences() != root_inf[i]:
                if i == self.id: # the agent has lost the influence
                    if p.num_influences() == 1:
                        lose_inf = -50
                    if p.num_influences() == 0:
                        lose_inf = -400
                else: # an opponent has lost the influence
                    if p.num_influences() == 1:
                        lose_inf = 30
                    elif p.num_influences() == 0:
                        lose_inf = 50
            break # a maximum of one player can lose an influences per state transition
        
        reward += lose_inf
        reward += (state.players[self.id].coins - self.root_state.players[self.id].coins) * 2
        
        return reward

class LookAheadAgent():
    def __init__(self, id):
        self.id = id
        self.name = "One Step Look Ahead Agent"
    def choice(self, state):
        blockPrint()
        if not state.players[self.id].check_player_in():
            return None
        look_ahead = LookAhead(state, self.id)
        look_ahead.search()
        enablePrint()
        return look_ahead.best_move()

def blockPrint():
    sys.stdout = open(os.devnull, 'w')
def enablePrint():
    sys.stdout = sys.__stdout__