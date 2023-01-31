import random
from game import *
import time

def main():

    num_players = 2
    deck = Deck()
    deck.shuffle()
    players = []
    for player_num in range(num_players):
        name = "Player " + str(player_num)
        players.append(Player(player_num, num_players, name)) # player.id will always match player's index in players
        deck.deal(players[player_num], times=2)

    count = 0
    while not is_winner(players):

        turn = count % num_players
        if check_player_in(players[turn]):
            for player in players:
                print(player.name, player.coins, player.num_influences(), player.cards, player.cards[0].showing, player.cards[1].showing)

            print("\n" + players[turn].name + "'s turn!")
            actions = get_actions(turn, players, deck)
            action = choice(actions, "Please choose action from:")
            # print("Possible actions:")
            # print(actions)
            print("Action taken: " + players[turn].name + " plays '" + action.__repr__() + "' claiming " + action.action_character)

            action_challenges = get_action_challenges(action, players)
            action_challenge = choice(action_challenges, "Please choose action challenge from:")
            # print("Possible challenges:")
            # print(action_challenges)
            print("Challenge taken:")
            print(action_challenge)
            if not (action_challenge == None):
                winner, loser = challenge_action(action_challenge.action, action_challenge.challenger) # handle challenge
                if winner.id == action.player.id: # if the winner is the one who was challenged
                    card_index = 0
                    if winner.cards[1].name == action.action_character:
                        card_index = 1
                    print(winner.name + " wins the challenge with " + winner.cards[card_index].name)
                    action.execute(success=True)
                    deck.append(winner.cards.pop(card_index))
                    deck.shuffle()
                    deck.deal(winner)
                    loser.lose_influence() # The loser can choose which card to turn over
                else: # the winner is the one who challenged the action
                    print(winner.name + " wins the challenge because " + loser.name + " does not have " + action.action_character)
                    loser.lose_influence() # Note: the loser has chosen a card to turn over to prove the challenge. Loser the same card that they chose to turn over
            else:
                counteractions = get_counteractions(players, action)
                # print("Possible counteractions:")
                # print(counteractions)
                counteraction = choice(counteractions, "Please choose counteraction from:")
                print("Counteraction taken: ")
                print(counteraction)
                if counteraction == None: # the action went unchallenged so if no one counteracts the action succeeds 
                    action.execute(success=True)
                else:
                    counteraction_challenges = get_counteraction_challenges(counteraction, players)
                    counteraction_challenge = choice(counteraction_challenges, "Please choose counteraction challenge from:")
                    # print("Possible challenges to counteraction:")
                    # print(counteraction_challenges)
                    print("Challenge to counteraction taken:")
                    print(counteraction_challenge)
                    if not (counteraction_challenge == None):
                        winner, loser = challenge_counteraction(counteraction_challenge.counteraction, counteraction_challenge.challenger) # handle challenge: if counteractor wins challenger loses influence 
                        #if winner is counteractor
                        if winner.id == counteraction_challenge.counteraction.counteractor:
                            print("Write this...")
                            card_index = 0
                            if winner.cards[1].name == counteraction_challenge.counteraction.claim:
                                card_index = 1
                            deck.append(winner.cards.pop(card_index))
                            deck.shuffle()
                            deck.deal(winner)
                            action.execute(success=False)
                            counteraction_challenge.challenger.lose_influence()
                        else: # if the winner is the challenger
                            print("Write this too...")
                            action.execute(success=True)
                            counteraction_challenge.counteraction.counteractor.lose_influence()

                    else: # If no one counters the counteraction it counteracts the action
                        action.execute(success=False)
        
        count += 1
    
    print("\n" + players[get_winner(players)].name + " wins the game!!!")

if __name__ == "__main__":
    main()