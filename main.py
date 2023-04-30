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
    agent_choices = {"Random":"random", "Random and does not bluff":"random_no_bluff", "Random and does not bluff or challenge":"random_no_bluff_no_challenge", "Income":"income", "AI-1: Lookahead (cheater)":"look_ahead", "AI-2: MCTS (cheater)":"mcts"}
    game_mode = choose_from_list(["I wish to play Coup", "I wish to battle computer agents against each other"])
    if game_mode == 0:
        print("How many opponents do you wish to play against?")
        n = choose_from_list(["One", "Two", "Three", "Four", "Five"])
        num_players = n+2
        if num_players == 2 or num_players == 3:
            agent_choices["AI-3: (does not cheat)"] = "mcts_uncertainty"
        agents[0] = "human"
        rand_opps = choose_from_list(["I wish to choose my opponents", "Don't tell me who I'm playing against"])
        if rand_opps == 0:
            for i in range(1,num_players):
                print(f"Please choose Player {i}'s agent:")
                agent = choose_from_list(list(agent_choices.keys()))
                a = "random"
                if agent == 1: a = "random_no_bluff"
                elif agent == 2: a = "random_no_bluff_no_challenge"
                elif agent == 3: a = "income"
                elif agent == 4: a = "look_ahead"
                elif agent == 5: a = "mcts"
                elif agent == 6: a = "mcts_uncertainty"
                agents[i] = a
        else:
            for i in range(1,num_players):
                agents[i] = random.choice(list(agent_choices.values()))
    else:
        battle = True
        print("How many players do you wish to battle against each other?")
        n = choose_from_list(["Two", "Three", "Four", "Five", "Six"])
        num_players = n+2
        if num_players == 2 or num_players == 3:
            agent_choices["AI-3: (does not cheat)"] = "mcts_uncertainty"

        rand_opps = choose_from_list(["I wish to choose each player", "Generate players randomly"])
        if rand_opps == 0:
            for i in range(0,num_players):
                print(f"Please choose Player {i}'s agent:")
                agent = choose_from_list(list(agent_choices.keys()))
                a = "random"
                if agent == 1: a = "random_no_bluff"
                elif agent == 2: a = "random_no_bluff_no_challenge"
                elif agent == 3: a = "income"
                elif agent == 4: a = "look_ahead"
                elif agent == 5: a = "mcts"
                elif agent == 6: a = "mcts_uncertainty"
                agents[i] = a
        else:
            agent_str = ""
            for i in range(0,num_players):
                c = random.choice(list(agent_choices.values()))
                agents[i] = c
                for key, value in agent_choices.items():
                    if value == c:
                        agent_str += f"Player {i}: {key}\n"
                        break
                
            print(agent_str)
            press_to_continue()
        
    state = State(num_players=num_players, agents=agents)
    while not state.is_winner():
        state.transition(battle=battle)
    winner = state.get_winner().id

    print("------------------------------------------------------------")
    print(f"Player {winner} wins the game!")
    
if __name__ == "__main__":
    main()

    # t_start = time.perf_counter()
    # t_stop = time.perf_counter()
    # t_elapsed = t_stop-t_start

    # for i in range(num_players):
    #     print((results[i]*100)/iterations)