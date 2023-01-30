import random

def main():
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
            print("Deck shuffled!")
        
        def deal(self, player, times=1):
            for i in range(times):
                player.cards.append(self.pop(0))

    class Player(object):
        def __init__(self, name=None):
            self.name = name
            self.coins = 2
            self.cards = []

        def __repr__(self):
            return self.name

    def check_player_in(player):
        if len(player.cards) <= 0:
            return False
        return True

    def check_coup(player, target):
        if len(player.cards) <= 0:
            return False
        if len(target.cards) <= 0:
            return False
        if player.coins < 7:
            return False
        return True

    def check_assassinate(player, target):
        if len(player.cards) <= 0:
            return False
        if len(target.cards) <= 0:
            return False
        if player.coins < 3:
            return False
        return True

    def check_steal(player, target):
        if len(player.cards) <= 0:
            return False
        if len(target.cards) <= 0:
            return False
        if player.coins < 1:
            return False
        return True
    
    def get_actions(current_player_index, players):
        actions = []
        player = players[current_player_index]
        if not check_player_in(player):
            return actions
        force_coup = False
        if player.coins >= 10:
            force_coup = True
        if not force_coup:
            actions.append(Action("Income", player))
            actions.append(Action("Foreign Aid", player))
            actions.append(Action("Tax", player))
            actions.append(Action("Exchange", player))
            for i in range(len(players)):
                if i == current_player_index:
                    continue
                if check_player_in(players[i]): # double checking player is in, this is already checked in individual action check functions
                    if check_coup(player, players[i]):
                        actions.append(Action("Coup", player, players[i]))
                    if check_assassinate(player, players[i]):
                        actions.append(Action("Assassinate", player, players[i]))
                    if check_steal(player, players[i]):
                        actions.append(Action("Steal", player, players[i]))
        else:
            for i in range(len(players)):
                if i == current_player_index:
                    continue
                if check_player_in(players[i]): # double checking player is in, this is already checked in individual action check functions
                    if check_coup(player, players[i]):
                        actions.append(Action("Coup", player, players[i]))

        return actions

    def income(player):
        player.coins += 1
    def foreign_aid(player):
        player.coins += 2
    def coup(player, target):
        player.coins -= 7
        target.cards.pop(0) # change this to allow target to choose which card to give up
    def tax(player):
        player.coins += 3
    def assassinate(player, target):
        player.coins -= 3
        target.cards.pop(0) # change this to allow target to choose which card to give up
    def steal(player, target):
        coins_to_take = 2
        if target.coins == 1:
            coins_to_take = 1
        target.coins -= coins_to_take
        player.coins += coins_to_take
    def exchange(player, deck):
        deck.deal(player, 2)
        player.cards.pop(0) # change this to allow player to choose which cards to keep
        player.cards.pop(0)

    def get_counteractions(actor_player_index, players, action):
        counteractions = []
        player = players[actor_player_index]
        if not check_player_in(player): # This should never happen
            return False
        for i in range(len(players)):
            if i == actor_player_index:
                continue
            if action.name == "Foreign Aid":
                counteractions.append(Counteraction(player, players[i], action, "Duke"))
        if action.name == "Assassinate":
            counteractions.append(Counteraction(player, action.target, action, "Contessa"))
        elif action.name == "Steal":
            counteractions.append(Counteraction(player, action.target, action, "Ambassador"))
            counteractions.append(Counteraction(player, action.target, action, "Captain"))

        return counteractions

    class Counteraction(object):
        def __init__(self, actor, counteractor, action, claim):
            self.actor = actor
            self.counteractor = counteractor
            self.action = action
            self.claim = claim
        def __repr__(self):
            return self.counteractor.name + " blocks " + self.action.__repr__() + " claiming " + self.claim

    class Action(object):
        def __init__(self, action_name, player, target=None):

            action_character = "None"
            blocked_by = []

            if action_name == "Foreign Aid":
                blocked_by.append("Duke")

            elif action_name == "Tax":
                action_character = "Duke"

            elif action_name == "Assassinate":
                action_character = "Assassin"
                blocked_by.append("Contessa")

            elif action_name == "Steal":
                action_character = "Captain"
                blocked_by.append("Ambassador")
                blocked_by.append("Captain")

            elif action_name == "Exchange":
                action_character = "Ambassador"
            
            self.name = action_name
            self.player = player
            self.target = target
            self.action_character = action_character
            self.blocked_by = blocked_by

        def __repr__(self):
            if self.target:
                if self.name == "Steal":
                    return self.name + " from " + self.target.name
                return self.name + " " + self.target.name
            return self.name

    deck = Deck()
    deck.shuffle()
    players = []
    num_players = 3
    for player_num in range(num_players):
        name = "Player " + str(player_num)
        players.append(Player(name))
        deck.deal(players[player_num], times=2)

    print(players)
    a = get_actions(0, players)
    print(a)
    a1 = a[1]
    print(a1)
    print(get_counteractions(0, players, a1))

if __name__ == "__main__":
    main()