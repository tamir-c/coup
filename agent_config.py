from agent import *
from mcts import *
from mcts_uncertainty import *
from look_ahead import *

def generate_agent(id, agent):
     # COMPLETE FOR ALL AGENTS
    if agent == None or agent == "random":
        return RandomAgent(id)
    if agent == None or agent == "random_no_bluff":
        return RandomNoBluffAgent(id)
    if agent == "human":
        return HumanAgent(id)
    if agent == "random_bluff_bias":
        return RandomBluffBiasAgent(id)
    if agent == "mcts":
        return MCTSAgent(id)
    if agent == "mcts_uncertainty":
        return MCTSUncertaintyAgent(id)
    if agent == "look_ahead":
        return LookAheadAgent(id)
    if agent == "income":
        return IncomeAgent(id)
    if agent == "random_no_bluff_no_challenge":
        return RandomNoBluffNoChallengeAgent(id)
    return RandomAgent(id)