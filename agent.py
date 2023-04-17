import random

class RandomAgent(object):
    def __init__(self, id):
        self.id = id
        self.name = "Random Agent"

    def choice(self, state):
        p = state.players[self.id]
        if state.stage == 0:
            if state.actor != self.id:
                raise Exception("Error: it is not this agent's turn to choose an action!")
            return random.choice(state.get_actions())
        elif state.stage == 1:
            return random.choice(state.get_action_challenges(p))
        elif state.stage == 2:
            return random.choice(state.get_counteractions(p))
        elif state.stage == 3:
            return random.choice(state.get_counteraction_challenges(p))

class RandomNoBluffAgent(object):
    def __init__(self):
        self.id = id
        self.name = "Random No Bluff Agent"

    def choice(self, list, state=None): # state should always be provided to this agent
        length = len(list)
        if length == 0:
            return None
        for i, item in enumerate(list):
            if state.stage == 0: # if choosing an action
                if item.action_character != "General Action":
                    if not (item.action_character in item.player.get_active_action_characters()):
                        list.pop(i)
            elif state.stage == 2: # if choosing a counteraction
                if item != None:
                    if not (item.claim in item.counteractor.get_active_action_characters()):
                        list.pop(i)
        return random.choice(list)
    
class RandomNoChallengeAgent(object):
    def __init__(self):
        self.id = id
        self.name = "Random No Challenge Agent"

    def choice(self, list, state=None): # state should always be provided to this agent
        length = len(list)
        if length == 0:
            return None
        if state.stage == 1 or state.stage == 3:
            return None
        return random.choice(list)

class RandomNoBluffNoChallengeAgent(object):
    def __init__(self):
        self.id = id
        self.name = "Random No Bluff No Challenge Agent"

    def choice(self, list, state=None): # state should always be provided to this agent
        length = len(list)
        if length == 0:
            return None
        
        if state.stage == 1 or state.stage == 3:
            return None
        
        for i, item in enumerate(list):
            if state.stage == 0: # if choosing an action
                if item.action_character != "General Action":
                    if not (item.action_character in item.player.get_active_action_characters()):
                        list.pop(i)
            elif state.stage == 2: # if choosing a counteraction
                if item != None:
                    if not (item.claim in item.counteractor.get_active_action_characters()):
                        list.pop(i)

        return random.choice(list)

class HumanAgent(object):
    def __init__(self, id):
        self.id = id
        self.name = "Human Agent"
    # choice function for human agent
    def choice(self, state):
        p = state.players[self.id]
        lst = None
        prt = ""
        if state.stage == 0:
            if state.actor != self.id:
                raise Exception("Error: it is not this agent's turn to choose an action!")
            prt = "Please choose action from: "
            lst = state.get_actions()
        elif state.stage == 1:
            prt = "Please choose action challenge from: "
            lst = state.get_action_challenges(p)
        elif state.stage == 2:
            prt = "Please choose counteraction from: "
            lst = state.get_counteractions(p)
        elif state.stage == 3:
            prt = "Please choose counteraction challenge from: "
            lst = state.get_counteraction_challenges(p)
        
        length = len(lst)
        if length == 0:
            return None
        if length == 1:
            return lst[0]

        print(prt)
        for i in range(length):
            print(str(i) + ": " + lst[i].__repr__())
        while True:
            c = input()
            if c.isdigit():
                if int(c) in range(length):
                    return lst[int(c)]
            print(f"Please enter a number in the range 0 to {length-1}.")
                    