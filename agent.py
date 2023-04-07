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
    def choice(self, list, message=""):
        length = len(list)
        if length == 0:
            return None
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