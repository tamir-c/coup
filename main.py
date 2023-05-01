from state import *
from game import *
from agent import *
from mcts import *
from mcts_uncertainty import *
from look_ahead import *

def main():
    battle = False
    num_players = 3 # default number of players
    agents = {}
    agent_choices = {"Random":"random", "Random and does not bluff":"random_no_bluff", "Random and does not bluff or challenge":"random_no_bluff_no_challenge", "Random but bluffs 30% of the time":"random_bluff_bias", "Income":"income", "AI-1: Lookahead (cheater)":"look_ahead", "AI-2: MCTS (cheater)":"mcts"}
    agent_str = ""
    game_mode = choose_from_list(["I wish to play Coup", "I wish to battle computer agents against each other"])
    rand_opps = 0
    if game_mode == 0:
        agents[0] = "human"
        print("How many opponents do you wish to play against?")
        n = choose_from_list(["One", "Two", "Three", "Four", "Five"])
        num_players = n+2
        if num_players == 2 or num_players == 3:
            agent_choices["AI-3: (does not cheat)"] = "mcts_uncertainty"
        
        rand_opps = choose_from_list(["I wish to choose my opponents", "Don't tell me who I'm playing against"])

        agent_str += f"Player 0: Human\n"
        for i in range(1,num_players):
            if rand_opps == 0:
                print(f"Please choose Player {i}'s agent:")
                agent = choose_from_list(list(agent_choices.keys()))
                values = list(agent_choices.values())
                a = values[agent]
                agents[i] = a
            else:
                a = random.choice(list(agent_choices.values()))
                agents[i] = a
            for key, value in agent_choices.items():
                if value == a:
                    agent_str += f"Player {i}: {key}\n"
                    break
        if rand_opps == 0:
            print("\nYou have chosen the following agents to play against:")
            print(agent_str)
            press_to_continue()

    else:
        battle = True
        print("How many players do you wish to battle against each other?")
        n = choose_from_list(["Two", "Three", "Four", "Five", "Six"])
        num_players = n+2
        if num_players == 2 or num_players == 3:
            agent_choices["AI-3: (does not cheat)"] = "mcts_uncertainty"

        rand_opps_2 = choose_from_list(["I wish to choose each player", "Generate players randomly"])
        
        for i in range(0,num_players):
            if rand_opps_2 == 0:
                print(f"Please choose Player {i}'s agent:")
                agent = choose_from_list(list(agent_choices.keys()))
                values = list(agent_choices.values())
                a = values[agent]
                agents[i] = a
            else:
                a = random.choice(list(agent_choices.values()))
                agents[i] = a
            for key, value in agent_choices.items():
                if value == a:
                    agent_str += f"Player {i}: {key}\n"
                    break
        print("\nYou are battling the following agents:")
        print(agent_str)
        press_to_continue()
        
    state = State(num_players=num_players, agents=agents)
    # State is transitioned until there is a winner
    while not state.is_winner():
        state.transition(battle=battle)
    winner = state.get_winner().id

    print("------------------------------------------------------------")
    print(f"Player {winner} wins the game!")
    if rand_opps == 1:
        press_to_continue()
        print("\nYou were playing against:")
        print(agent_str)

    
if __name__ == "__main__":
    main()

    # t_start = time.perf_counter()
    # t_stop = time.perf_counter()
    # t_elapsed = t_stop-t_start

    # for i in range(num_players):
    #     print((results[i]*100)/iterations)