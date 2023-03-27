import random
from game import *
import time
import copy


def game(state):
    while not is_winner(state.players):

        turn = state.actor
        if check_player_in(state.players[turn]):
            for player in state.players:
                print(player.name, player.coins, player.num_influences(), player.cards, player.cards[0].showing, player.cards[1].showing)

            print("\n" + state.players[turn].name + "'s turn!")
            actions = get_actions(turn, state.players, state.deck)
            action = choice(actions, "Please choose action from:")
            print("Possible actions:")
            print(actions)
            print("Action taken: " + state.players[turn].name + " plays '" + action.__repr__() + "' claiming " + action.action_character)

            action_challenges = get_action_challenges(action, state.players)
            action_challenge = choice(action_challenges, "Please choose action challenge from:")
            print("Possible challenges:")
            print(action_challenges)
            print("Challenge taken:")
            print(action_challenge)
            if not (action_challenge == None):
                winner, loser = challenge_action(action_challenge.action, action_challenge.challenger) # handle challenge
                if winner.id == action.player.id: # if the winner is the one who was challenged
                    card_index = 0
                    if winner.cards[1].name == action.action_character and winner.cards[1].showing == False:
                        card_index = 1
                    print(winner.name + " wins the challenge with " + winner.cards[card_index].name)
                    action.execute(success=True)
                    state.deck.append(winner.cards.pop(card_index))
                    state.deck.shuffle()
                    state.deck.deal(winner)
                    cardToLose = choice(loser.get_active_cards(), "Please choose card to lose from: ")
                    card_index = 0
                    if loser.cards[1] == cardToLose:
                        card_index = 1
                    loser.lose_influence(card_index) # The loser can choose which card to turn over
                else: # the winner is the one who challenged the action. The action fails so the actor loses an influence and play continues
                    print(winner.name + " wins the challenge because " + loser.name + " does not have " + action.action_character)
                    cardToLose = choice(loser.get_active_cards(), "Please choose card to lose from: ")
                    card_index = 0
                    if loser.cards[1] == cardToLose:
                        card_index = 1
                    loser.lose_influence(card_index)
            else:
                counteractions = get_counteractions(state.players, action)
                print("Possible counteractions:")
                print(counteractions)
                counteraction = choice(counteractions, "Please choose counteraction from:")
                print("Counteraction taken: ")
                print(counteraction)
                if counteraction == None: # the action went unchallenged so if no one counteracts the action succeeds 
                    action.execute(success=True)
                else:
                    counteraction_challenges = get_counteraction_challenges(counteraction, state.players)
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
                            state.deck.append(winner.cards.pop(card_index))
                            state.deck.shuffle()
                            state.deck.deal(winner)
                            action.execute(success=False)
                            counteraction_challenge.challenger.lose_influence()
                        else: # if the winner is the challenger
                            print("Write this too...")
                            action.execute(success=True)
                            counteraction_challenge.counteraction.counteractor.lose_influence()

                    else: # If no one counters the counteraction it counteracts the action
                        action.execute(success=False)
        
        state.increment_turn()
    
    print("\n" + state.players[get_winner(state.players)].name + " wins the game!!!")

def main():
    new = True
    if new:
        s = State()
        game(s)
    else: # resume already existing game from state string - not a priority
        pass
        # string = "2-6-0-0-1-0-9-4-1-3-0-1-0-0-0-0-2"


if __name__ == "__main__":
    main()