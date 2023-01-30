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

    class Action(object):
        def __init__(self, type):
            self.type = type
            action_name = ""
            action_character = "None"
            blocked_by = ""
            self.blocked_by
            cost = 0
            if self.type == 0:
                action_name = "Income"
            elif self.type == 1:
                action_name = "Foreign Aid"
            elif self.type == 2:
                action_name = "Coup"
            elif self.type == 3:
                action_name = "Tax"
                action_character = "Duke"
            elif self.type == 4:
                action_name = "Assassinate"
                action_character = "Assassin"
            elif self.type == 5:
                action_name = "Steal"
                action_character = "Captain"
            elif self.type == 6:
                action_name = "Exchange"
                action_character = "Ambassador"
            
            self.name = action_name
            self.action_character = "action_character"
            self.blocked_by = blocked_by

        def income(player):
            player.coins += 1
        def foreign_aid(player):
            player.coins += 2
        def coup(player, target):
            if player.coins < 7:
                return False
            player.coins -= 7
            target.cards.pop(0) # change this to allow target to choose which card to give up

    deck = Deck()
    deck.shuffle()
    players = []
    num_players = 2
    for player_num in range(num_players):
        name = "Player " + str(player_num)
        players.append(Player(name))
        deck.deal(players[player_num], times=2)

    print(players)
    print(players[0].cards)
    print(players[1].cards)
    print(deck)

if __name__ == "__main__":
    main()