import random

class State(object):
    def __init__(self, state_string = "", num_players = 2):
        if num_players <= 1 or num_players > 6:
            num_players = 2
        if state_string == "":    
            self.num_players = num_players
            self.players = []
            self.deck = Deck()
            self.deck.shuffle()
            self.actor = 0
            for i in range(self.num_players):
                self.players.append(Player(i, self.num_players)) # player.id will always match player's index in players
                self.deck.deal(self.players[i], times=2)
        else:
            self.num_players, self.players, self.deck, self.actor = load_game_state(state_string)

    def increment_turn(self):
        self.actor = (self.actor + 1) % self.num_players

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
        # super().__init__()
        for i in range(5): # A standard deck has 3 of each of the 5 character types
            for j in range(3):
                self.append(Card(i))
    
    def shuffle(self):
        random.shuffle(self)
    
    def deal(self, player, times=1):
        for i in range(times):
            player.cards.append(self.pop(0))
    
    def deal_character(self, player, type):
        for i in range(len(self)):
            if self[i].type == type:
                player.cards.append(self.pop(i))
                break
            

class Player(object):
    def __init__(self, id, num_players, name=None, coins=None):
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
        self.agent = Agent()

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


    # Removes one the player's influences where card_id is the preference of which card the player loses
    def lose_influence(self, inf_to_lose=0):
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
    # To do! FIX SELF.TYPE
    def __init__(self, action_name, player, deck, target=None):

        action_character = "General Action"
        blocked_by = []
        self.type = 0

        if action_name == "Foreign Aid":
            self.type = 1
            blocked_by.append("Duke")

        elif action_name == "Tax":
            self.type = 2
            action_character = "Duke"

        elif action_name == "Assassinate":
            self.type = 3
            action_character = "Assassin"
            blocked_by.append("Contessa")

        elif action_name == "Steal":
            self.type = 4
            action_character = "Captain"
            blocked_by.append("Ambassador")
            blocked_by.append("Captain")

        elif action_name == "Exchange":
            self.type = 5
            action_character = "Ambassador"
        
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

def choice(list, message="Please choose from: ", rand=True):
    length = len(list)
    if length == 0:
        return None
    if length == 1:
        return list[0]
    if rand:
        return random.choice(list)
    print(message)
    for i in range(length):
        print(str(i) + ": " + list[i].__repr__())
    while True:
        c = input()
        if c.isdigit():
            if int(c) in range(length):
                return list[int(c)]

def check_player_in(player):
    if player.num_influences() <= 0:
        return False
    return True

def check_coup(player, target):
    if check_player_in(player) == False:
        return False
    if check_player_in(target) == False:
        return False
    if player.coins < 7:
        return False
    return True

def check_assassinate(player, target):
    if check_player_in(player) == False:
        return False
    if check_player_in(target) == False:
        return False
    if player.coins < 3:
        return False
    return True

def check_steal(player, target):
    if check_player_in(player) == False:
        return False
    if check_player_in(target) == False:
        return False
    if target.coins < 1:
        return False
    return True

def get_actions(current_player_index, players, deck):
    actions = []
    player = players[current_player_index]
    force_coup = False
    if player.coins >= 10:
        force_coup = True
    if not force_coup:
        actions.append(Action("Income", player, deck))
        actions.append(Action("Foreign Aid", player, deck))
        actions.append(Action("Tax", player, deck))
        actions.append(Action("Exchange", player, deck))
        # Each check_[action] function verifies the actor and target are in, and that the game state allows for this action to occur
        for i in range(len(players)):
            if i == current_player_index:
                continue
            if check_coup(player, players[i]):
                actions.append(Action("Coup", player, deck, players[i]))
            if check_assassinate(player, players[i]):
                actions.append(Action("Assassinate", player, deck, players[i]))
            if check_steal(player, players[i]):
                actions.append(Action("Steal", player, deck, players[i]))
    else:
        for i in range(len(players)):
            if i == current_player_index:
                continue
            if check_coup(player, players[i]):
                actions.append(Action("Coup", player, deck, players[i]))

    return actions

def income(player, success):
    if success:
        print(player.name + " gains 1 coin through Income!")
        player.coins += 1
def foreign_aid(player, success):
    if success:
        print(player.name + " gains 2 coins through Foreign Aid!")
        player.coins += 2
def coup(player, target, success):
    player.coins -= 7
    print(player.name + " spends 7 coins to Coup!")
    if success:
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
    # if success: 
        # print(player.name + " exchanges two cards from the deck!")
        # deck.deal(player, 2)
        # exchangable = []
        # for card in player.cards:
        #     if card.showing == False:
        #         exchangable.append(card)
        # if len(exchangable) == 3:
        #     c0 = choice(exchangable, "Please choose one card to keep:")
        #     c1 = player.cards[1]
        #     exchangable.remove(c0)
        #     if player.cards[0].showing:
        #         c1 = c0
        #         c0 = player.cards[0]
        # elif len(exchangable) == 4:
        #     c0 = choice(exchangable, "Please choose 1st out of 2 cards to keep:")
        #     exchangable.remove(c0)
        #     c1 = choice(exchangable, "Please choose 2nd out of 2 cards to keep:")
        #     exchangable.remove(c1)
        # player.cards = [c0, c1]
        # print(player.cards)
        # print(exchangable)
        # for c in exchangable:
        #     deck.append(exchangable.pop(0))
        # deck.shuffle()
def get_counteractions(players, action):
    counteractions = []
    player = action.player
    counteractions.append(None)
    for i in range(len(players)):
        if i == action.player.id:
            continue
        if action.name == "Foreign Aid":
            if (check_player_in(players[i])):
                counteractions.append(Counteraction(action, players[i], "Duke"))
    # It has already been checked that the action's target is still in upon creating the action
    if action.name == "Assassinate":
        counteractions.append(Counteraction(action, action.target, "Contessa"))
    elif action.name == "Steal":
        counteractions.append(Counteraction(action, action.target, "Ambassador"))
        counteractions.append(Counteraction(action, action.target, "Captain"))

    return counteractions

# Returns winner, loser
def challenge_action(action, challenger):
    names = [action.player.cards[0].name, action.player.cards[1].name]
    if action.action_character in names:
        return action.player, challenger
    else:
        return challenger, action.player

def challenge_counteraction(counteraction, challenger):
    names = [counteraction.counteractor.cards[0].name, counteraction.counteractor.cards[1].name]
    if counteraction.claim in names:
        return counteraction.counteractor, challenger
    return challenger, counteraction.counteractor

def get_action_challenges(action, players):
    action_challenges = []
    player = action.player
    action_challenges.append(None)
    for i in range(len(players)):
        if i == action.player.id:
            continue
        if action.name == "Tax" or action.name == "Assassinate" or action.name == "Steal" or action.name == "Exchange":
            if (check_player_in(players[i])):
                action_challenges.append(ActionChallenge(action, players[i]))
    return action_challenges

def get_counteraction_challenges(counteraction, players):
    counteraction_challenges = []
    counteraction_challenges.append(None)
    for i in range(len(players)):
        if i == counteraction.counteractor.id:
            continue
        if check_player_in(players[i]):
            counteraction_challenges.append(CounteractionChallenge(counteraction, players[i]))
    return counteraction_challenges

def is_winner(players):
    in_players = 0
    for player in players:
        if check_player_in(player):
            in_players += 1
    if in_players == 1:
        return True
    return False

def get_winner(players):
    if is_winner(players):
        for player in players:
            if check_player_in(player):
                return player.id
    else:
        return -1
    
def load_game_state(string):
    p = string.split("-")
    num_players = int(p[0])
    players = []
    deck = Deck()
    for i in range(num_players):
        coins = p[1+5*i]
        player = Player(i, num_players)
        deck.deal_character(player, int(p[2+5*i]))
        if p[3+5*i] == 0:
            player.cards[0].showing = False
        else:
            player.cards[0].showing = True
        deck.deal_character(player, int(p[4+5*i]))
        if p[5+5*i] == 0:
            player.cards[0].showing = False
        else:
            player.cards[0].showing = True
        players.append(player)
    
    count = int(p[num_players*5 + 1])
    return num_players, players, deck, count
