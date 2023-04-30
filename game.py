import random
import sys, os
from agent_config import *

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
    def __init__(self, id, num_players, coins=None, agent="random"):
        self.agent = generate_agent(id, agent)
        self.id = id
        self.name = "Player " + str(self.id)
        if coins==None:
            if num_players == 2:
                self.coins = 1
            else:
                self.coins = 2
        else:
            self.coins = coins
        self.cards = []

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
    
    # deals cards of the same type to a player - used in mcts_uncertainty
    def redeal_opponents(self, type):
        s0 = self.cards[0].showing
        s1 = self.cards[1].showing
        self.cards[0] = Card(type)
        self.cards[0].showing = s0
        self.cards[1] = Card(type)
        self.cards[1].showing = s1

    # Removes one of the player's influences
    def lose_influence(self, is_print=True):
        inf = self.num_influences()
        if inf == 1:
            if self.cards[0].showing:
                self.cards[1].showing = True
            else:
                self.cards[0].showing = True
        else: # The player loses influence 0 by default if they have two active influences
            self.cards[0].showing = True
        if is_print: print(self.name + " loses an influence!")

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

    def execute(self, success, is_print=True):
        prt = is_print
        if self.name == "Income":
            income(self.player, success, is_print=prt)
        elif self.name == "Foreign Aid":
            foreign_aid(self.player, success, is_print=prt)
        elif self.name == "Coup":
            coup(self.player, self.target, success, is_print=prt)
        elif self.name == "Tax":
            tax(self.player, success, is_print=prt)
        elif self.name == "Assassinate":
            assassinate(self.player, self.target, success, is_print=prt)
        elif self.name == "Steal":
            steal(self.player, self.target, success, is_print=prt)
        elif self.name == "Exchange":
            exchange(self.player, self.deck, success, is_print=prt)

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

def income(player, success, is_print=True):
    if success:
        if is_print: print(player.name + " gains 1 coin through Income!")
        player.coins += 1
def foreign_aid(player, success, is_print=True):
    if success:
        if is_print: print(player.name + " gains 2 coins through Foreign Aid!")
        player.coins += 2
def coup(player, target, success, is_print=True):
    if success:
        player.coins -= 7
        if is_print: print(player.name + " spends 7 coins to Coup!")
        if is_print: print(player.name + " Coups " + target.name)
        target.lose_influence(is_print) # change this to allow target to choose which card to give up
def tax(player, success, is_print=True):
    if success:
        if is_print: print(player.name + " collects 3 coins through tax!")
        player.coins += 3
def assassinate(player, target, success, is_print=True):
    player.coins -= 3
    if is_print: print(player.name + " spends 3 coins to assassinate!")
    if success:
        if is_print: print(player.name + " assassinates " + target.name)
        target.lose_influence(is_print) # change this to allow target to choose which card to give up
def steal(player, target, success, is_print=True):
    if success:
        coins_to_take = 2
        if target.coins == 1:
            coins_to_take = 1
        if is_print: print(player.name + " steals " + str(coins_to_take) + " coins from " + target.name)
        target.coins -= coins_to_take
        player.coins += coins_to_take
def exchange(player, deck, success, is_print=True):
    tax(player, success, is_print=is_print)

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

# returns index of chosen element in list i.e. elements listed number - 1
def choose_from_list(lst):
    length = len(lst)
    if length == 0:
        return None
    if length == 1:
        return 0

    for i in range(length):
        print(f"{i+1}: {lst[i]}")
    while True:
        c = input(f"Please enter a number in the range 1 to {length}: ")
        if c.isdigit():
            if int(c) in range(1, length+1):
                return int(c)-1

def press_to_continue():
    cont = False
    while not cont:
        inp = input("Press ENTER to continue: ")
        if inp == "":
            return