from game import *
import random
from tabulate import tabulate
import numpy as np

class State(object):
    def __init__(self, state_string = "", num_players = 2, agents={}):
        if num_players <= 1 or num_players > 6:
            num_players = 3
        if state_string == "":    
            self.num_players = num_players
            self.players = []
            self.deck = Deck()
            self.deck.shuffle()

            self.actor = 0 # actor index
            self.action = None
            self.challenge = None
            self.is_challenge = False
            self.counteraction = None
            self.is_counteraction = False
            self.counteraction_challenge = None
            self.is_counteraction_challenge = False
            self.stage = 0

            for i in range(self.num_players):
                # if the player's agent is not specified it will default to RandomAgent() (set in Player init)
                self.players.append(Player(i, self.num_players, agent=agents.get(i))) # player.id will always match player's index in players
                self.deck.deal(self.players[i], times=2)

    def increment_turn(self):
        found_next = False
        while (not found_next) and (not self.is_winner()):
            self.actor = (self.actor + 1) % self.num_players
            if self.players[self.actor].check_player_in():
                found_next = True

    def get_actions(self):
        player = self.players[self.actor]
        actions = []
        force_coup = False
        if player.coins >= 10:
            force_coup = True
        if not force_coup:
            actions.append(Action("Income", player, self.deck))
            actions.append(Action("Foreign Aid", player, self.deck))
            actions.append(Action("Tax", player, self.deck))
            actions.append(Action("Exchange", player, self.deck))
            # Each check_[action] function verifies the actor and target are in, and that the game state allows for this action to occur
            for i in range(len(self.players)):
                if i == player.id:
                    continue
                if check_coup(player, self.players[i]):
                    actions.append(Action("Coup", player, self.deck, self.players[i]))
                if check_assassinate(player, self.players[i]):
                    actions.append(Action("Assassinate", player, self.deck, self.players[i]))
                if check_steal(player, self.players[i]):
                    actions.append(Action("Steal", player, self.deck, self.players[i]))
        else:
            for i in range(len(self.players)):
                if i == player.id:
                    continue
                if check_coup(player, self.players[i]):
                    actions.append(Action("Coup", player, self.deck, self.players[i]))
        return actions
    
    # Returns a list of all possible counteractions available to a player
    # If none available, or counteractor and actor are the same player, returns a list containing just None
    def get_counteractions(self, c_actor):
        counteractions = []
        counteractions.append(None)
        if not (c_actor == self.action.player):
            if self.action.name == "Foreign Aid":
                if (c_actor.check_player_in()):
                    counteractions.append(Counteraction(self.action, c_actor, "Duke"))
            # It has already been checked that the action's target is still in upon creating the action
            if self.action.name == "Assassinate" and c_actor == self.action.target:
                counteractions.append(Counteraction(self.action, c_actor, "Contessa"))
            elif self.action.name == "Steal" and c_actor == self.action.target:
                counteractions.append(Counteraction(self.action, c_actor, "Ambassador"))
                counteractions.append(Counteraction(self.action, c_actor, "Captain"))
        return counteractions
    
    # Returns a list of all possible action challenges for a given player
    # If none available, or challenger and actor are same player, or the challenger is not in, returns a list containing just None
    def get_action_challenges(self, challenger):
        action_challenges = []
        action_challenges.append(None)
        if challenger != self.action.player:
            if self.action.name == "Tax" or self.action.name == "Assassinate" or self.action.name == "Steal" or self.action.name == "Exchange":
                if challenger.check_player_in():
                    action_challenges.append(ActionChallenge(self.action, challenger))
        return action_challenges

    # Returns a list of all available counteraction challenges for a given player
    # If none available, or challenger and counteractor are the same player, or challenger is not in, returns a list containing just None
    def get_counteraction_challenges(self, challenger):
        counteraction_challenges = []
        counteraction_challenges.append(None)
        if self.counteraction == None:
            return counteraction_challenges
        if challenger == self.counteraction.action.player: # IMPORTANT: we modify the game so the actor cannot challenge a counteraction, making the transitions easier to model
            return counteraction_challenges
        if challenger != self.counteraction.counteractor:
            if challenger.check_player_in():
                counteraction_challenges.append(CounteractionChallenge(self.counteraction, challenger))
        return counteraction_challenges
    
    def is_winner(self):
        in_players = 0
        for player in self.players:
            if player.check_player_in():
                in_players += 1
        if in_players <= 1:
            return True
        return False
    
    def get_winner(self):
        if self.is_winner():
            for player in self.players:
                if player.check_player_in():
                    return player
        else:
            return None

    def transition(self, a1, a2, a3):
        if self.is_winner():
            return

        # r = list(range(self.num_players))
        # random.shuffle(r)
        turn = self.actor
        if self.players[turn].check_player_in():

            if (self.challenge): # if a challenge has occured:
                winner, loser = challenge_action(a2.action, a2.challenger) # handle challenge
                if winner == a1.player: # if the winner is the one who was challenged
                    # finds the card index of the actors card that won the challenge
                    card_index = 0
                    if winner.cards[1].name == a1.action_character and winner.cards[1].showing == False:
                        card_index = 1
                    a1.execute(success=True)
                    self.deck.append(winner.cards.pop(card_index))
                    self.deck.shuffle()
                    self.deck.deal(winner)
                    loser.lose_influence()
                else: # the winner is the one who challenged the action. The action fails so the actor loses an influence and play continues
                    loser.lose_influence()
            
            else: # a2 must be a counteraction
                if a2 == None: # the action went unchallenged so if no one counteracts the action succeeds 
                    self.action.execute(success=True)
                else: # a2 stores the counteraction
                    if self.counteraction_challenge:
                        winner, loser = challenge_counteraction(a3.counteraction, a3.challenger) # handle challenge: if counteractor wins challenger loses influence 
                        #if winner is counteractor
                        if winner == a3.counteraction.counteractor:
                            card_index = 0
                            if winner.cards[1].name == a3.counteraction.claim and winner.cards[1].showing == False:
                                card_index = 1
                            self.deck.append(winner.cards.pop(card_index))
                            self.deck.shuffle()
                            self.deck.deal(winner)
                            a1.execute(success=False)
                            a3.challenger.lose_influence()
                        else: # if the winner is the challenger
                            a1.execute(success=True)
                            a3.counteraction.counteractor.lose_influence()

                    else: # If no one challenges the counteraction, the counteraction succeeds so the action fails
                        a1.execute(success=False)
        self.stage = 0
        self.action = None
        self.challenge = None
        self.is_challenge = False
        self.counteraction = None
        self.is_counteraction = False
        self.counteraction_challenge = None
        self.is_counteraction_challenge = False
        if not self.is_winner():
            self.increment_turn()

    # OLD transition function kept for reference
    def transition_old(self, is_print=False):

        if self.is_winner():
            return
        
        human = False
        for p in self.players: 
            if p.agent.name == "Human Agent":
                human = True
        r = list(range(self.num_players))
        if not human: random.shuffle(r)

        turn = self.actor
        if self.players[turn].check_player_in():
           
            self.print_obs()
            if human: press_to_continue()
            print("\n" + self.players[turn].__repr__() + "'s turn!")
             # for debugging
            # for player in self.players:
            #     # print(player.name, player.coins, player.num_influences(), player.cards, player.cards[0].showing, player.cards[1].showing)
            #     print(f"{player.name} {player.coins} {player.cards[0] if player.cards[0].showing else 'Not Showing'} {player.cards[1] if player.cards[1].showing else 'Not Showing'}")
                
            self.stage = 0
            self.action = self.players[turn].agent.choice(state=self)

            print(self.action)
            print(self.is_winner())
            print("Action taken: " + self.players[turn].name + " plays '" + self.action.__repr__() + "' claiming " + self.action.action_character)
            if human: press_to_continue()
            self.stage = 1
            for i in r:
                self.challenge = self.players[i].agent.choice(state=self)
                if self.challenge: # if a player has challenged, break - only one player can challenge an action in a play
                    break

            print("Challenge taken:")
            print(self.challenge)
            if human: press_to_continue()
            if self.challenge: # if a challenge has occured:
                winner, loser = challenge_action(self.challenge.action, self.challenge.challenger) # handle challenge
                if winner == self.action.player: # if the winner is the one who was challenged
                    # finds the card index of the actors card that won the challenge
                    card_index = 0
                    if winner.cards[1].name == self.action.action_character and winner.cards[1].showing == False:
                        card_index = 1
                    print(winner.name + " wins the challenge with " + winner.cards[card_index].name)
                    if human: press_to_continue()
                    self.action.execute(success=True)
                    if human: press_to_continue()
                    self.deck.append(winner.cards.pop(card_index))
                    self.deck.shuffle()
                    self.deck.deal(winner)
                    loser.lose_influence()
                    if human: press_to_continue()
                else: # the winner is the one who challenged the action. The action fails so the actor loses an influence and play continues
                    print(winner.name + " wins the challenge because " + loser.name + " does not have " + self.action.action_character)
                    if human: press_to_continue()
                    loser.lose_influence()
                    if human: press_to_continue()
            else: # there were no challenges so game moves to counteractions
                self.stage = 2
                for i in r:
                    self.counteraction = self.players[i].agent.choice(state=self)
                    if self.counteraction:
                        break

                print("Counteraction taken: ")
                print(self.counteraction)
                if human: press_to_continue()
                if not self.counteraction: # the action went unchallenged and no one counteracted so the action succeeds 
                    self.action.execute(success=True)
                    if human: press_to_continue()
                else: # players can choose to challenge the counteraction
                    self.stage = 3
                    for i in r:
                        self.counteraction_challenge = self.players[i].agent.choice(state=self)
                        if self.counteraction_challenge:
                            break

                    print("Challenge to counteraction taken:")
                    print(self.counteraction_challenge)
                    if human: press_to_continue()
                    if self.counteraction_challenge:
                        winner, loser = challenge_counteraction(self.counteraction_challenge.counteraction, self.counteraction_challenge.challenger) # handle challenge: if counteractor wins challenger loses influence 
                        #if winner is counteractor
                        if winner == self.counteraction_challenge.counteraction.counteractor:
                            print(winner.__repr__() + " wins with " + self.counteraction_challenge.counteraction.claim + "!")
                            if human: press_to_continue()
                            card_index = 0
                            if winner.cards[1].name == self.counteraction_challenge.counteraction.claim and winner.cards[1].showing == False:
                                card_index = 1
                            self.deck.append(winner.cards.pop(card_index))
                            self.deck.shuffle()
                            self.deck.deal(winner)
                            self.action.execute(success=False)
                            self.counteraction_challenge.challenger.lose_influence()
                            if human: press_to_continue()
                        else: # if the winner is the challenger
                            print(winner.__repr__() + " wins because " + loser.__repr__() + " does not have " + self.counteraction_challenge.counteraction.claim + "!")
                            if human: press_to_continue()
                            self.action.execute(success=True)
                            self.counteraction_challenge.counteraction.counteractor.lose_influence()
                            if human: press_to_continue()

                    else: # If no one challenges the counteraction, the counteraction succeeds so the action fails
                        self.action.execute(success=False)
                        if human: press_to_continue()

        self.stage = 0
        self.action = None
        self.challenge = None
        self.counteraction = None
        self.counteraction_challenge = None
        if not self.is_winner():
            self.increment_turn()

    # print the state for debugging purposes
    def print(self):
        for p in self.players:
            s0 = "showing" if p.cards[0].showing else "not showing"
            s1 = "showing" if p.cards[1].showing else "not showing"
            print(f"{p.name} has {p.cards[0]} - {s0} and {p.cards[1]} - {s1}")
    
    # def random_sim(self):
    #     r = list(range(self.num_players))
    #     random.shuffle(r)

    #     while not self.is_winner():
    #         a1 = random.choice(self.get_actions())
    #         self.action = a1
    #         a2 = None
    #         a3 = None
    #         for i in r:
    #             a2 = random.choice(self.get_action_challenges(self.players[i]))
    #             if a2:
    #                 self.is_challenge = True
    #                 self.challenge = a2
    #                 break
    #         if not a2:
    #             for i in r:
    #                 a2 = random.choice(self.get_counteractions(self.players[i]))
    #                 if a2:
    #                     self.is_counteraction = True
    #                     self.counteraction = a2
    #                     break
    #         if self.is_counteraction:
    #             for i in r:
    #                 a3 = random.choice(self.get_counteraction_challenges(self.players[i]))
    #                 if a3:
    #                     self.is_counteraction_challenge = True
    #                     self.counteraction_challenge = a3
    #                     break
    #         self.transition(a1, a2, a3)
    #     return self.get_winner().id
    
    def random_transition(self, node):
        if self.is_winner():
            for player in self.players:
                print(player.num_influences())
            raise Exception("This is a terminal state!")
        a2 = None
        a3 = None
        if self.stage == 0:
            self.action = node.action
            for p in self.players:
                a2 = random.choice(self.get_action_challenges(p))
                if a2:
                    self.challenge = a2
                    break
            if not self.challenge:
                for p in self.players:
                    a2 = random.choice(self.get_counteractions(p))
                    if a2:
                        self.counteraction = a2
                        break
            if self.counteraction:
                for p in self.players:
                    a3 = random.choice(self.get_counteraction_challenges(p))
                    if a3:
                        self.counteraction_challenge = a3
                        break
            return self.transition(self.action, a2, a3)
        elif self.stage == 1: # choosing whether to challenge or not
            if node.action:
                self.challenge = node.action
            return self.transition(self.action, self.challenge, None)
        elif self.stage == 2: # choosing whether to counteract or not. We assume we might choose to challenge counteraction if made independently or counteracting
            if node.action:
                self.counteraction = node.action
            for p in self.players:
                a3 = random.choice(self.get_counteraction_challenges(p))
                if a3:
                    self.counteraction_challenge = a3
                    break
            return self.transition(self.action, self.counteraction, a3)
        elif self.stage == 3: # chosing whether to challenge counteraction or not
            if node.action:
                self.counteraction_challenge = node.action
            return self.transition(self.action, self.counteraction, self.counteraction_challenge)
    
    # prints a table of the current game state that would be observable to every player
    def print_obs(self): 
        table = [['Player Name','Coins','Inf 1', 'Inf 1 Active?', 'Inf 2', 'Inf 2 Active?', 'Player Still In?']]
        for player in self.players:
            inf_1 = f"{player.cards[0] if player.cards[0].showing else 'Not Showing'}"
            inf_1_active = f"{not player.cards[0].showing}"
            inf_2 = f"{player.cards[1] if player.cards[1].showing else 'Not Showing'}"
            inf_2_active = f"{not player.cards[1].showing}"
            still_in = f"{player.check_player_in()}"
            if player.agent.name == "Human Agent":
                inf_1 = f"{player.cards[0]}"
                inf_2 = f"{player.cards[1]}"
            table.append([player.name, player.coins, inf_1, inf_1_active, inf_2, inf_2_active, still_in])
        print(tabulate(table, headers="firstrow", tablefmt="pretty"))
                



# def load_game_state(string):
#     p = string.split("-")
#     num_players = int(p[0])
#     players = []
#     deck = Deck()
#     for i in range(num_players):
#         coins = p[1+5*i]
#         player = Player(i, num_players)
#         deck.deal_character(player, int(p[2+5*i]))
#         if p[3+5*i] == 0:
#             player.cards[0].showing = False
#         else:
#             player.cards[0].showing = True
#         deck.deal_character(player, int(p[4+5*i]))
#         if p[5+5*i] == 0:
#             player.cards[0].showing = False
#         else:
#             player.cards[0].showing = True
#         players.append(player)
    
#     count = int(p[num_players*5 + 1])
#     return num_players, players, deck, count