import random
from abc import ABC, abstractmethod

# TODO: split actions, challenges, counteractions, and counteraction challenges into lists that belong to each agent

# class Agent(ABC):
#     def __init__(self, type=0):
#         self.type = type
#     @abstractmethod
#     def choice(self):
#         pass
    
class RandomAgent(object):
    def choice(self, list, message="", state=None):
        length = len(list)
        if length == 0:
            return None
        return random.choice(list)
    
class RandomNoBluffAgent(object):
    def choice(self, list, message="", state=None): # state should always be provided to this agent
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
    def choice(self, list, message="", state=None): # state should always be provided to this agent
        length = len(list)
        if length == 0:
            return None
        if state.stage == 1 or state.stage == 3:
            return None
        return random.choice(list)

class RandomNoBluffNoChallengeAgent(object):
    def choice(self, list, message="", state=None): # state should always be provided to this agent
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
    # choice function for human agent
    def choice(self, list, message="Please choose from: "):
        length = len(list)
        if length == 0:
            return None
        if length == 1:
            return list[0]
        print(message)
        for i in range(length):
            print(str(i) + ": " + list[i].__repr__())
        while True:
            c = input()
            if c.isdigit():
                if int(c) in range(length):
                    return list[int(c)]