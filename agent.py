import random

# TODO: split actions, challenges, counteractions, and counteraction challenges into lists that belong to each agent

class Agent(object):
    def __init__(self, type=0):
        self.type = type
    
    def choice(list):
        length = len(list)
        if length == 0:
            return None
        if length == 1:
            return 0
        return random.choice(list)

    