import random
from copy import deepcopy
from game import *
import time
# from state import *
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

class LookAhead:
    def __init__(self, state, id):
        self.id = id
        self.root_state = deepcopy(state)
        self.root = Node(None, None)

    def expand(self):
        state = deepcopy(self.root_state) 
        if state.stage == 0:
            actions = state.get_actions()
        elif state.stage == 1:
            actions = state.get_action_challenges(state.players[self.id])
        elif state.stage == 2:
            actions = state.get_counteractions(state.players[self.id])
        elif state.stage == 3:
            actions = state.get_counteraction_challenges(state.players[self.id])
        children = [Node(action, self.root) for action in actions]
        self.root.add_children(children)
        return True

    def get_reward(self, state):
        reward = 0
        root_inf = 0
        new_inf = 0
        for p in self.root_state.players:
            root_inf += p.num_influences()
        for p in state.players:
            new_inf += p.num_influences()
        if state.players[self.id].num_influences() == self.root_state.players[self.id].num_influences(): # if the agent has not lost an influence
            reward += (root_inf - new_inf) * 100
        else:
            reward -= 100
            
        reward += (self.root_state.players[self.id].coins - state.players[self.id].coins) * 10
        return reward
    
    def search(self, time_limit=0.05):
        self.expand()
        t_start = time.process_time()
        while time.process_time() - t_start < time_limit:
            state = deepcopy(self.root_state)
            child = random.choice(self.root.children) 
            state.random_transition(child)
            reward = self.get_reward(state)
            child.reward += reward
            child.num_sims += 1
    
    def best_move(self):
        if self.root_state.is_winner():
            return -1
        if len(self.root.children) == 1:
            return self.root.children[0].action
        max_value = self.root.children[0].reward / self.root.children[0].num_sims
        for c in self.root.children:
            if c.reward/c.num_sims > max_value:
                max_value = c.reward / c.num_sims
        max_nodes = [c for c in self.root.children if c.reward/c.num_sims == max_value]
        best_child = random.choice(max_nodes)
        return best_child.action

class LookAheadAgent():
    def __init__(self, id):
        self.id = id
        self.name = "One Step Look Ahead Agent"
    def choice(self, state):
        if not state.players[self.id].check_player_in():
            return None
        look_ahead = LookAhead(state, self.id)
        look_ahead.search()
        for c in look_ahead.root.children:
            print("-----------------------")
            print(c)
            print(f"num children = {len(look_ahead.root.children)}")
            print(f"{c.action} {str(c.reward)}")
            print("-----------------------")
        return look_ahead.best_move()
    
