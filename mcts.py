import random
from copy import deepcopy
import numpy as np
from game import *
from agent import *
import time

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
            max_value = children[0].value()
            for c in children:
                if c.value() > max_value:
                    max_value = c.value()
            max_nodes = [c for c in children if c.value() == max_value]
            node = random.choice(max_nodes)
            # select node to explore given the following:
            # if stage == 0 we are selecting an action
            # if stage == 1 we are selecting a challenge
            # if stage == 2 we are selecting a counteraction
            # if stage == 3 we are selecting a counteraction challenge

            a2 = None
            a3 = None
            if state.stage == 0:
                for p in state.players:
                    a2 = random.choice(get_action_challenges(node.action, p))
                    if a2:
                        state.is_challenge = True
                        state.challenge = a2
                        break
                if not a2:
                    for p in state.players:
                        a2 = random.choice(state.get_counteractions(state.players[self.id]))
                        if a2:
                            state.is_counteraction = True
                            state.counteraction = a2
                if state.is_counteraction:
                    for p in state.players:
                        a3 = get_counteraction_challenges(a2, p)
                    if a3:
                        state.is_counteraction_challenge = True
                state.transition(node.action, a2, a3)
            elif state.stage == 1: # choosing whether to challenge or not
                state.transition(state.action, node.action, None)
            elif state.stage == 2: # choosing whether to counteract or not. We assume we might choose to challenge counteraction if made independently or counteracting
                for p in state.players:
                    a3 = random.choice(get_counteraction_challenges(node.action))
                    if a3:
                        state.is_counteraction_challenge = True
                        state.counteraction_challenge = a3
                        break
                state.transition(state.action, node.action, a3)
            elif state.stage == 3:
                state.transition(state.action, state.counteraction, node.action)

            if node.num_sims == 0:
                return node, state

        if self.expand(node, state):
            node = random.choice(node.children)
            # state.action = node.action
            if state.stage == 0:
                state.action = node.action
                a2 = random.choice(get_action_challenges(node.action, state.players[self.id]))
                if a2:
                    state.challenge = 1
                if not a2:
                    a2 = random.choice(state.get_counteractions(state.players[self.id]))
                    if a2:
                        state.counteraction = 1
                a3 = None
                if state.counteraction:
                    a3 = get_counteraction_challenges(a2)
                    if a3:
                        state.counteraction_challenge = 1
                state.transition(node.action, a2, a3)
            elif state.stage == 1:
                state.transition(state.action, node.action, None)
            elif state.stage == 2:
                a3 = random.choice(get_counteraction_challenges(node.action))
                state.transition(state.action, node.action, a3)
            elif state.stage == 3:
                state.transition(state.action, state.counteraction, node.action)

        return node, state
    
    def expand(self, parent, state):
        if state.is_winner():
            return False
        if state.stage == 0:
            actions = state.get_actions()
        elif state.stage == 1:
            actions = get_action_challenges(state.action, state.players[self.id])
        elif state.stage == 2:
            actions = state.get_counteractions(state.action, state.players[self.id])
        elif state.stage == 3:
            actions = state.get_counteraction_challenges(state.counteraction, state.players[self.id])
        children = [Node(action, parent) for action in actions]
        parent.add_children(children)

        return True
    
    def roll_out(self, state):
        # while not state.is_winner():
        #     actions = state.get_actions()
        #     a = random.choice(actions)

        return state.random_sim() # plays game out until the end and returns winner.id
    
    def back_propagate(self, node, turn, outcome):
        if outcome == self.id: # if mcts won
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

    def search(self, time_limit = 1):
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
        
        max_value = self.root.children[0].num_sims
        for c in self.root.children:
            if c.num_sims > max_value:
                max_value = c.num_sims
        max_nodes = [c for c in self.root.children if c.num_sims == max_value]
        best_child = random.choice(max_nodes)
        return best_child.action