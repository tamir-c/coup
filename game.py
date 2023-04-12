import random
from agent import *

class State(object):
    def __init__(self, state_string = "", num_players = 2, agents={}):
        if num_players <= 1 or num_players > 6:
            num_players = 2
        if state_string == "":    
            self.num_players = num_players
            self.players = []
            self.deck = Deck()
            self.deck.shuffle()

            self.actor = 0 # actor index
            self.action = None
            self.challenge = None
            self.counteraction = None
            self.counteraction_challenge = None
            self.stage = 0

            for i in range(self.num_players):
                self.players.append(Player(i, self.num_players, agent=agents.get(i))) # player.id will always match player's index in players
                self.deck.deal(self.players[i], times=2)
        else:
            self.num_players, self.players, self.deck, self.actor = load_game_state(state_string)

    def increment_turn(self):
        found_next = False
        while not found_next:
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
    
    def is_winner(self):
        in_players = 0
        for player in self.players:
            if player.check_player_in():
                in_players += 1
        if in_players == 1:
            return True
        return False
    
    def get_winner(self):
        if self.is_winner():
            for player in self.players:
                if player.check_player_in():
                    return player
        else:
            return None

    def transition(self, action):
        if action == None:
            self.increment_turn()
            self.stage = 0
            self.action = None
            self.challenge = None
            self.counteraction = None
            self.counteraction_challenge = None
            return
        
        r = list(range(self.num_players))
        random.shuffle(r)

        turn = self.actor
        self.action = action
        if self.players[turn].check_player_in():
            # actions = self.get_actions(self.players[turn])
            # self.action = self.players[turn].agent.choice(actions, "Please choose action from:", state=self)
            self.stage = 1
            for i in r:
                action_challenges = get_action_challenges(self.action, self.players[i], self.players)
                self.challenge = self.players[i].agent.choice(action_challenges, "Please choose action challenge from:", state=self)
                if not (self.challenge == None): # if a player has challenged, break - only one player can challenge an action in a play
                    break

            if not (self.challenge == None): # if a challenge has occured:
                winner, loser = challenge_action(self.challenge.action, self.challenge.challenger) # handle challenge
                if winner == self.action.player: # if the winner is the one who was challenged
                    # finds the card index of the actors card that won the challenge
                    card_index = 0
                    if winner.cards[1].name == self.action.action_character and winner.cards[1].showing == False:
                        card_index = 1
                    self.action.execute(success=True)
                    self.deck.append(winner.cards.pop(card_index))
                    self.deck.shuffle()
                    self.deck.deal(winner)
                    loser.lose_influence()
                else: # the winner is the one who challenged the action. The action fails so the actor loses an influence and play continues
                    loser.lose_influence()
            else:
                self.stage = 2
                for i in r:
                    counteractions = self.get_counteractions(self.players[i])
                    self.counteraction = self.players[i].agent.choice(counteractions, "Please choose counteraction from:", state=self)
                    if not (self.counteraction == None):
                        break

                if self.counteraction == None: # the action went unchallenged so if no one counteracts the action succeeds 
                    self.action.execute(success=True)
                else:
                    self.stage = 3
                    for i in r:
                        counteraction_challenges = get_counteraction_challenges(self.counteraction, self.players[i], self.players)
                        self.counteraction_challenge = self.players[i].agent.choice(counteraction_challenges, "Please choose counteraction challenge from:", state=self)
                        if not (self.counteraction_challenge == None):
                            break

                    if not (self.counteraction_challenge == None):
                        winner, loser = challenge_counteraction(self.counteraction_challenge.counteraction, self.counteraction_challenge.challenger) # handle challenge: if counteractor wins challenger loses influence 
                        #if winner is counteractor
                        if winner == self.counteraction_challenge.counteraction.counteractor:
                            card_index = 0
                            if winner.cards[1].name == self.counteraction_challenge.counteraction.claim and winner.cards[1].showing == False:
                                card_index = 1
                            self.deck.append(winner.cards.pop(card_index))
                            self.deck.shuffle()
                            self.deck.deal(winner)
                            self.action.execute(success=False)
                            self.counteraction_challenge.challenger.lose_influence()
                        else: # if the winner is the challenger
                            self.action.execute(success=True)
                            self.counteraction_challenge.counteraction.counteractor.lose_influence()

                    else: # If no one challenges the counteraction, the counteraction succeeds so the action fails
                        self.action.execute(success=False)
        self.increment_turn()
        self.stage = 0
        self.action = None
        self.challenge = None
        self.counteraction = None
        self.counteraction_challenge = None

class Card(object):
        def __init__(self, type):
            self.type = type
            self.showing = False
            card_name = ""
            if self.type == 0:
                card_name = "Duke"
            elif self.type == 1:
                card_name = "Assassin"
            elif self.type == 2:
                card_name = "Ambassador"
            elif self.type == 3:
                card_name = "Captain"
            elif self.type == 4:
                card_name = "Contessa"
            self.name = card_name
        def __repr__(self):
            return self.name

class Deck(list):
    def __init__(self):
        for i in range(5): # A standard deck has 3 of each of the 5 character types
            for j in range(3):
                self.append(Card(i))
    
    def shuffle(self):
        random.shuffle(self)
    
    def deal(self, player, times=1):
        if len(player.cards) >= 2:
            return
        for i in range(times):
            if len(player.cards) < 2:
                player.cards.append(self.pop(0))
    
    def deal_character(self, player, type):
        if len(player.cards) >= 2:
            return
        for i in range(len(self)):
            if self[i].type == type:
                player.cards.append(self.pop(i))
                break
            
class Player(object):
    def __init__(self, id, num_players, name=None, coins=None, agent=RandomAgent()):
        if agent == None:
            agent = RandomAgent() #### COULD CAUSE AN ISSUE
        self.id = id
        self.name = name
        if self.name == None:
            self.name = "Player " + str(self.id)
        if coins==None:
            if num_players == 2:
                self.coins = 1
            else:
                self.coins = 2
        else:
            self.coins = coins
        self.cards = []
        self.agent = agent

    def __repr__(self):
        return self.name

    def num_influences(self):
        count = 2
        if self.cards[0].showing:
            count -= 1
        if self.cards[1].showing:
            count -= 1
        return count
    
    def get_active_cards(self):
        active_cards = []
        for c in self.cards:
            if c.showing == False:
                active_cards.append(c)
        return active_cards
    
    def get_active_action_characters(self):
        active_cards = self.get_active_cards()
        return [c.name for c in active_cards]

    # Removes one of the player's influences
    def lose_influence(self):
        inf = self.num_influences()
        if inf == 1:
            if self.cards[0].showing:
                self.cards[1].showing = True
            else:
                self.cards[0].showing = True
        else: # The player loses influence 0 by default if they have two active influences
            # lose = choice(self.cards, "Please choose card to lose and reval to the rest of the players:")
            # lose.showing = True
            self.cards[0].showing = True
        print(self.name + " loses an influence!")

    def check_player_in(self):
        if self.num_influences() <= 0:
            return False
        return True

class ActionChallenge(object):
    def __init__(self, action, challenger):
        self.action = action
        self.challenger = challenger
    def __repr__(self):
        return self.challenger.name + " " + "challenges " + "'" + self.action.__repr__() + "'"

class CounteractionChallenge(object):
    def __init__(self, counteraction, challenger):
        self.counteraction = counteraction
        self.challenger = challenger
    def __repr__(self):
        return self.challenger.name + " " + "challenges " + "'" + self.counteraction.__repr__() + "'"

class Counteraction(object):
    def __init__(self, action, counteractor, claim):
        self.counteractor = counteractor
        self.action = action
        self.claim = claim
    def __repr__(self):
        return self.counteractor.name + " blocks " + self.action.__repr__() + " claiming " + self.claim

class Action(object):
    def __init__(self, action_name, player, deck, target=None):

        action_character = "General Action"
        blocked_by = []
        if action_name == "Income":
            self.type = 0

        elif action_name == "Foreign Aid":
            self.type = 1
            blocked_by.append("Duke")

        elif action_name == "Coup":
            self.type = 2

        elif action_name == "Tax":
            self.type = 3
            action_character = "Duke"

        elif action_name == "Assassinate":
            self.type = 4
            action_character = "Assassin"
            blocked_by.append("Contessa")

        elif action_name == "Exchange":
            self.type = 5
            action_character = "Ambassador"

        elif action_name == "Steal":
            self.type = 6
            action_character = "Captain"
            blocked_by.append("Ambassador")
            blocked_by.append("Captain")

        self.name = action_name
        self.player = player
        self.target = target
        self.action_character = action_character
        self.blocked_by = blocked_by
        self.deck = deck

    def __repr__(self):
        if self.target:
            if self.name == "Steal":
                return self.name + " from " + self.target.name
            return self.name + " " + self.target.name
        return self.name

    def execute(self, success):
        if self.name == "Income":
            income(self.player, success)
        elif self.name == "Foreign Aid":
            foreign_aid(self.player, success)
        elif self.name == "Coup":
            coup(self.player, self.target, success)
        elif self.name == "Tax":
            tax(self.player, success)
        elif self.name == "Assassinate":
            assassinate(self.player, self.target, success)
        elif self.name == "Steal":
            steal(self.player, self.target, success)
        elif self.name == "Exchange":
            exchange(self.player, self.deck, success)

def check_coup(player, target):
    if player.check_player_in() == False:
        return False
    if target.check_player_in() == False:
        return False
    if player.coins < 7:
        return False
    return True

def check_assassinate(player, target):
    if player.check_player_in() == False:
        return False
    if target.check_player_in() == False:
        return False
    if player.coins < 3:
        return False
    return True

def check_steal(player, target):
    if player.check_player_in() == False:
        return False
    if target.check_player_in() == False:
        return False
    if target.coins < 1:
        return False
    return True

def income(player, success):
    if success:
        print(player.name + " gains 1 coin through Income!")
        player.coins += 1
def foreign_aid(player, success):
    if success:
        print(player.name + " gains 2 coins through Foreign Aid!")
        player.coins += 2
def coup(player, target, success):
    if success:
        player.coins -= 7
        print(player.name + " spends 7 coins to Coup!")
        print(player.name + " Coups " + target.name)
        target.lose_influence() # change this to allow target to choose which card to give up
def tax(player, success):
    if success:
        print(player.name + " collects 3 coins through tax!")
        player.coins += 3
def assassinate(player, target, success):
    player.coins -= 3
    print(player.name + " spends 3 coins to assassinate!")
    if success:
        print(player.name + " assassinates " + target.name)
        target.lose_influence() # change this to allow target to choose which card to give up
def steal(player, target, success):
    if success:
        coins_to_take = 2
        if target.coins == 1:
            coins_to_take = 1
        print(player.name + " steals " + str(coins_to_take) + " coins from " + target.name)
        target.coins -= coins_to_take
        player.coins += coins_to_take
def exchange(player, deck, success):
    tax(player, success)

# Returns winner, loser
def challenge_action(action, challenger):
    names = []
    if action.player.cards[0].showing == False:
        names.append(action.player.cards[0].name)
    if action.player.cards[1].showing == False:
        names.append(action.player.cards[1].name)
    if action.action_character in names:
        return action.player, challenger
    else:
        return challenger, action.player

def challenge_counteraction(counteraction, challenger):
    names = []
    if counteraction.counteractor.cards[0].showing == False:
        names.append(counteraction.counteractor.cards[0].name)
    if counteraction.counteractor.cards[1].showing == False:
        names.append(counteraction.counteractor.cards[1].name)
    if counteraction.claim in names:
        return counteraction.counteractor, challenger
    return challenger, counteraction.counteractor

# Returns a list of all possible action challenges for a given player
# If none available, or challenger and actor are same player, or the challenger is not in, returns a list containing just None
def get_action_challenges(action, challenger, players):
    action_challenges = []
    action_challenges.append(None)
    if not (challenger == action.player):
        if action.name == "Tax" or action.name == "Assassinate" or action.name == "Steal" or action.name == "Exchange":
            if (challenger.check_player_in()):
                action_challenges.append(ActionChallenge(action, challenger))
    return action_challenges

# Returns a list of all available counteraction challenges for a given player
# If none available, or challenger and counteractor are the same player, or challenger is not in, returns a list containing just None
def get_counteraction_challenges(counteraction, challenger, players):
    counteraction_challenges = []
    counteraction_challenges.append(None)
    if challenger == counteraction.action.player: # IMPORTANT: we modify the game so the actor cannot challenge a counteraction, making the transitions easier to model
        return counteraction_challenges
    if not (challenger == counteraction.counteractor):
        if challenger.check_player_in():
            counteraction_challenges.append(CounteractionChallenge(counteraction, challenger))
    return counteraction_challenges
    
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

def transition(state):
    r = list(range(state.num_players))
    random.shuffle(r)

    turn = state.actor
    if state.players[turn].check_player_in():
        for player in state.players:
            print(player.name, player.coins, player.num_influences(), player.cards, player.cards[0].showing, player.cards[1].showing)
        state.stage = 0
        print("\n" + state.players[turn].name + "'s turn!")
        actions = state.get_actions()
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
                counteractions = state.get_counteractions(state.players[i])
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