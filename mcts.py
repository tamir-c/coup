import random
from copy import deepcopy
import numpy as np
from game import *
import time
from state import *
from agent import *

# Significant portions of code found from
# https://www.harrycodes.com/blog/monte-carlo-tree-search

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
    def __init__(self, state, id = 0):
        self.id = id
        self.root_state = deepcopy(state)
        self.root = Node(None, None)
        self.temp_actor = None
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0

    def select_node(self):
        node = self.root
        state = deepcopy(self.root_state)

        while len(node.children) != 0: # these nodes have already been expanded
            children = node.children
            max_value = children[0].value()
            for c in children:
                if c.value() > max_value:
                    max_value = c.value()
            max_nodes = [c for c in children if c.value() == max_value]

            # node = random.choice(max_nodes)
            node = random.choice(children) # RANDOMLY SELECT ONE OF THE ROOT STATE'S CHILDREN
            # print(f"{node.action} {state.stage}")
            # select node to explore given the following:
            # if stage == 0 we are selecting an action
            # if stage == 1 we are selecting a challenge
            # if stage == 2 we are selecting a counteraction
            # if stage == 3 we are selecting a counteraction challenge

            self.random_transition(node, state)
            node.temp_actor = state.actor
            if node.num_sims == 0:
                return node, state

        if self.expand(node, state): # if a node is being expanded for the first time
            node = random.choice(node.children)
            self.random_transition(node, state)
            node.temp_actor = state.actor

        return node, state
    
    # are we expanding too deep such that nodes and states do not always coincide with the same player's turn?
    def expand(self, parent, state): 
        if state.is_winner():
            return False
        if parent != self.root:
            return False
        if state.stage == 0:
            actions = state.get_actions()
            # print(state.actor)
            # print(actions)
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
    
    def roll_out(self, state):
        for i, p in enumerate(state.players):
            p.agent = RandomAgent(i)
        while not state.is_winner():
            state.transition_old() # plays game out until the end and returns winner.id
        return state.get_winner().id
    
    def back_propagate(self, node, turn, outcome): # turn is WRONG! NEEDS TO BE FIXED
        if outcome == self.id: # if mcts won
            reward = 1
        else:
            reward = 0
        
        while node is not None:
            node.num_sims += 1
            node.num_wins += reward
            node = node.parent
            # if node.temp_actor == self.id:
            #     reward = 1
            # else:
            #     reward = 0

    def search(self, time_limit = 0.1):
        t_start = time.process_time()
        n_rollouts = 0
        while time.process_time() - t_start < time_limit:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            self.back_propagate(node, state.actor, outcome) # state.actor is WRONG! could have been causing the issues
            n_rollouts += 1

        run_time = time.process_time() - t_start
        self.run_time = run_time
        self.num_rollouts = n_rollouts

    def best_move(self):
        if self.root_state.is_winner():
            return -1
        
        # max_value = self.root.children[0].num_sims
        # for c in self.root.children:
        #     if c.num_sims > max_value:
        #         max_value = c.num_sims
        # max_nodes = [c for c in self.root.children if c.num_sims == max_value]
        # best_child = random.choice(max_nodes)
        max_value = self.root.children[0].num_wins
        for c in self.root.children:
            if c.num_wins > max_value:
                max_value = c.num_wins
        max_nodes = [c for c in self.root.children if c.num_wins == max_value]
        best_child = random.choice(max_nodes)
        return best_child.action
    
    def random_transition(self, node, state):
        a2 = None
        a3 = None
        if state.stage == 0:
            state.action = node.action
            for p in state.players:
                a2 = random.choice(state.get_action_challenges(p))
                if a2:
                    state.is_challenge = True
                    state.is_counteraction = False
                    state.challenge = a2
                    break
            if not state.is_challenge:
                for p in state.players:
                    a2 = random.choice(state.get_counteractions(p))
                    if a2:
                        state.is_counteraction = True
                        state.is_challenge = False
                        state.counteraction = a2
                        break
            if state.is_counteraction:
                for p in state.players:
                    a3 = random.choice(state.get_counteraction_challenges(p))
                    if a3:
                        state.is_counteraction_challenge = True
                        break
            state.transition(state.action, a2, a3)
        elif state.stage == 1: # choosing whether to challenge or not
            if node.action:
                state.is_challenge = True
            state.transition(state.action, node.action, None)
        elif state.stage == 2: # choosing whether to counteract or not. We assume we might choose to challenge counteraction if made independently or counteracting
            if node.action:
                state.is_counteraction = True
                state.counteraction = node.action
            for p in state.players:
                a3 = random.choice(state.get_counteraction_challenges(p))
                if a3:
                    state.is_counteraction_challenge = True
                    break
            state.transition(state.action, node.action, a3)
        elif state.stage == 3: # chosing whether to challenge counteraction or not
            if node.action:
                state.is_counteraction_challenge = True
            state.transition(state.action, state.counteraction, node.action)

class MCTSAgent(object):
    def __init__(self, id):
        self.id = id
        self.name = "MCTS Agent"

    def choice(self, state, msg=""):
        mcts = MCTS(state, self.id)
        mcts.search()
        return mcts.best_move()