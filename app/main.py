import random
from game import *
import time
import copy
import sys, os
from agent import *

# Functions to block and enable calls to print (used to speed up testing agents)
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
def enablePrint():
    sys.stdout = sys.__stdout__

def game(state):
    blockPrint()
    while not is_winner(state.players):

        r = list(range(state.num_players))
        random.shuffle(r)

        turn = state.actor
        if check_player_in(state.players[turn]):
            for player in state.players:
                print(player.name, player.coins, player.num_influences(), player.cards, player.cards[0].showing, player.cards[1].showing)
            state.stage = 0
            print("\n" + state.players[turn].name + "'s turn!")
            actions = get_actions(state.players[turn], state.players, state.deck)
            print("Possible actions:")
            print(actions)
            state.action = state.players[turn].agent.choice(actions, "Please choose action from:", state=state)
            print("Action taken: " + state.players[turn].name + " plays '" + state.action.__repr__() + "' claiming " + state.action.action_character)
            state.stage = 1
            for i in r:
                action_challenges = get_action_challenges(state.action, state.players[i], state.players)
                print("Possible challenges for " + state.players[i].name + ":")
                print(action_challenges)
                state.challenge = state.players[i].agent.choice(action_challenges, "Please choose action challenge from:", state=state)
                if not (state.challenge == None): # if a player has challenged, break - only one player can challenge an action in a play
                    break

            print("Challenge taken:")
            print(state.challenge)
            if not (state.challenge == None): # if a challenge has occured:
                winner, loser = challenge_action(state.challenge.action, state.challenge.challenger) # handle challenge
                if winner == state.action.player: # if the winner is the one who was challenged
                    # finds the card index of the actors card that won the challenge
                    card_index = 0
                    if winner.cards[1].name == state.action.action_character and winner.cards[1].showing == False:
                        card_index = 1
                    print(winner.name + " wins the challenge with " + winner.cards[card_index].name)
                    state.action.execute(success=True)
                    state.deck.append(winner.cards.pop(card_index))
                    state.deck.shuffle()
                    state.deck.deal(winner)
                    loser.lose_influence()
                else: # the winner is the one who challenged the action. The action fails so the actor loses an influence and play continues
                    print(winner.name + " wins the challenge because " + loser.name + " does not have " + state.action.action_character)
                    loser.lose_influence()
            else:
                state.stage = 2
                for i in r:
                    counteractions = get_counteractions(state.players[i], state.players, state.action)
                    print("Possible counteractions for " + state.players[i].name + ":")
                    print(counteractions)
                    state.counteraction = state.players[i].agent.choice(counteractions, "Please choose counteraction from:", state=state)
                    print("Counteraction taken: ")
                    print(state.counteraction)
                    if not (state.counteraction == None):
                        break

                if state.counteraction == None: # the action went unchallenged so if no one counteracts the action succeeds 
                    state.action.execute(success=True)
                else:
                    state.stage = 3
                    for i in r:
                        counteraction_challenges = get_counteraction_challenges(state.counteraction, state.players[i], state.players)
                        print("Possible challenges to counteraction for " + state.players[i].name + ":")
                        print(counteraction_challenges)
                        state.counteraction_challenge = state.players[i].agent.choice(counteraction_challenges, "Please choose counteraction challenge from:", state=state)
                        if not (state.counteraction_challenge == None):
                            break

                    print("Challenge to counteraction taken:")
                    print(state.counteraction_challenge)
                    if not (state.counteraction_challenge == None):
                        winner, loser = challenge_counteraction(state.counteraction_challenge.counteraction, state.counteraction_challenge.challenger) # handle challenge: if counteractor wins challenger loses influence 
                        #if winner is counteractor
                        if winner == state.counteraction_challenge.counteraction.counteractor:
                            print(winner.__repr__() + " wins with " + state.counteraction_challenge.counteraction.claim + "!")
                            card_index = 0
                            if winner.cards[1].name == state.counteraction_challenge.counteraction.claim and winner.cards[1].showing == False:
                                card_index = 1
                            state.deck.append(winner.cards.pop(card_index))
                            state.deck.shuffle()
                            state.deck.deal(winner)
                            state.action.execute(success=False)
                            state.counteraction_challenge.challenger.lose_influence()
                        else: # if the winner is the challenger
                            print(winner.__repr__() + " wins because " + loser.__repr__() + " does not have " + state.counteraction_challenge.counteraction.claim + "!")
                            state.action.execute(success=True)
                            state.counteraction_challenge.counteraction.counteractor.lose_influence()

                    else: # If no one challenges the counteraction, the counteraction succeeds so the action fails
                        state.action.execute(success=False)
        
        state.increment_turn()

    winner = state.players[get_winner(state.players)]
    print("\n" + winner.name + " wins the game!!!")
    enablePrint()
    return winner

def main():
    iterations = 1000
    num_players=3
    results = [0 for i in range(num_players)]
    for i in range(iterations):
        s = State(num_players=num_players, 
                  agents={},
                #   agents={0:RandomNoBluffAgent(), 7:RandomNoChallengeAgent(), 7:RandomNoChallengeAgent()}
                  )
        result = game(s)
        results[result.id] += 1
    for i in range(num_players):
        print((results[i]*100)/iterations)


    #else: # resume already existing game from state string - not a priority
    #   pass
        # string = "2-6-0-0-1-0-9-4-1-3-0-1-0-0-0-0-2"


if __name__ == "__main__":
    main()