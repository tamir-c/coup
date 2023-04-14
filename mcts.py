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

        while len(node.children) != 0: # these nodes have already been expanded
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

            self.random_transition(node, state)
            if node.num_sims == 0:
                return node, state

        if self.expand(node, state): # if a node is being expanded for the first time
            node = random.choice(node.children)
            self.random_transition(node, state)

        return node, state
    
    def expand(self, parent, state):
        if state.is_winner():
            return False
        if state.stage == 0:
            actions = state.get_actions()
        elif state.stage == 1:
            actions = get_action_challenges(state.action, state.players[self.id])
        elif state.stage == 2:
            actions = state.get_counteractions(state.players[self.id])
        elif state.stage == 3:
            actions = get_counteraction_challenges(state.counteraction, state.players[self.id])
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

    def search(self, time_limit = 0.01):
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
    
    def random_transition(self, node, state):
        a2 = None
        a3 = None
        if state.stage == 0:
            state.action = node.action
            for p in state.players:
                a2 = random.choice(get_action_challenges(node.action, p))
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
                    a3 = random.choice(get_counteraction_challenges(a2, p))
                    if a3:
                        state.is_counteraction_challenge = True
                        break
            state.transition(node.action, a2, a3)
        elif state.stage == 1: # choosing whether to challenge or not
            if node.action:
                state.is_challenge = True
            state.transition(state.action, node.action, None)
        elif state.stage == 2: # choosing whether to counteract or not. We assume we might choose to challenge counteraction if made independently or counteracting
            if node.action:
                state.is_counteraction = True
                state.counteraction = node.action
            for p in state.players:
                a3 = random.choice(get_counteraction_challenges(node.action, p))
                if a3:
                    state.is_counteraction_challenge = True
                    break
            state.transition(state.action, node.action, a3)
        elif state.stage == 3: # chosing whether to challenge counteraction or not
            if node.action:
                state.is_counteraction_challenge = True
            state.transition(state.action, state.counteraction, node.action)

def main():
    blockPrint()
    num_players=3
    iterations = 10
    results = [0 for i in range(num_players)]
    
    for i in range(iterations):
        state = State(num_players=num_players, agents={})
        while not state.is_winner():
            a1 = None
            a2 = None
            a3 = None
            state.stage = 0
            if state.actor == 0:
                mcts = MCTS(state)
                mcts.search()
                a1 = mcts.best_move()
                enablePrint()
                state.print()
                print(a1)
                blockPrint()
                state.action = a1
                for p in state.players:
                    a2 = random.choice(get_action_challenges(a1, p))
                    if a2:
                        state.is_challenge = True
                        state.challenge = a2
                        break
                if not a2:
                    for p in state.players:
                        a2 = random.choice(state.get_counteractions(p))
                        if a2:
                            state.is_counteraction = True
                            state.counteraction = a2
                            break
                if state.is_counteraction:
                    for p in state.players:
                        a3 = random.choice(get_counteraction_challenges(a2, p))
                        if a3:
                            state.is_counteraction_challenge = True
                            state.counteraction_challenge = a3
                            break
            else:
                a1 = random.choice(state.get_actions())
                state.action = a1
                state.stage = 1
                for p in state.players:
                    if p.id == 0:
                        mcts = MCTS(state)
                        mcts.search()
                        a2 = mcts.best_move()
                        enablePrint()
                        print(a2)
                        # state.print()
                        blockPrint()
                    elif not a2:
                        a2 = random.choice(get_action_challenges(a1, p))
                    if a2:
                        state.is_challenge = True
                        state.challenge = a2
                        break
                if not a2:
                    state.stage = 2
                    for p in state.players:
                        if p.id == 0:
                            mcts = MCTS(state)
                            mcts.search()
                            a2 = mcts.best_move()
                            enablePrint()
                            print(a2)
                            # state.print()
                            blockPrint()
                        elif not a2:
                            a2 = random.choice(state.get_counteractions(p))
                        if a2:
                            state.is_counteraction = True
                            state.counteraction = a2
                            break
                    if a2:
                        state.stage = 3
                        for p in state.players:
                            if p.id == 0:
                                mcts = MCTS(state)
                                mcts.search()
                                a3 = mcts.best_move()
                                enablePrint()
                                print(a3)
                                # state.print()
                                blockPrint()
                            elif not a3:
                                a3 = random.choice(get_counteraction_challenges(a2, p))
                            if a3:
                                state.counteraction_challenge = a3
                                state.is_counteraction_challenge = True
                                break
                
            state.transition(a1, a2, a3)
        results[state.get_winner().id] += 1
    enablePrint()
    for i in range(num_players):
        print(results[i])
        # print((results[i]*100)/iterations)

if __name__ == "__main__":
    main()