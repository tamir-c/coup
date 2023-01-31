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
        def __init__(self, id, name=None):
            self.id = id
            self.name = name
            self.coins = 2
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

        def lose_influence(self, card_id = 0):
            if card_id == 0 and self.cards[0].showing == True:
                self.cards[1].showing = True
            elif card_id == 0 and self.cards[0].showing == False:
                self.cards[0].showing = True
            elif card_id == 1 and self.cards[1].showing == True:
                self.cards[0].showing = True
            else:
                self.cards[1].showing = True

    def check_player_in(player):
        if player.num_influences() <= 0:
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

    def income(player, success):
        if success:
            player.coins += 1
    def foreign_aid(player, success):
        if success:
            player.coins += 2
    def coup(player, target, success):
        player.coins -= 7
        if success:
            target.cards[0].showing = True # change this to allow target to choose which card to give up
    def tax(player, success):
        if success:
            player.coins += 3
    def assassinate(player, target, success):
        player.coins -= 3
        if success:
            target.cards[0].showing = True # change this to allow target to choose which card to give up
    def steal(player, target, success):
        if success:
            coins_to_take = 2
            if target.coins == 1:
                coins_to_take = 1
            target.coins -= coins_to_take
            player.coins += coins_to_take
    def exchange(player, deck, success):
        if success:
            deck.deal(player, 2)
            player.cards.pop(0) # change this to allow player to choose which cards to keep
            player.cards.pop(0)

    def get_counteractions(players, action):
        counteractions = []
        player = action.player
        if not check_player_in(player): # This should never happen
            return False
        counteractions.append(None)
        for i in range(len(players)):
            if i == action.player.id:
                continue
            if action.name == "Foreign Aid":
                counteractions.append(Counteraction(action, players[i], "Duke"))
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
        if not check_player_in(player): # This should never happen
            return False
        action_challenges.append(None)
        for i in range(len(players)):
            if i == action.player.id:
                continue
            if action.name == "Tax" or action.name == "Assassinate" or action.name == "Steal" or action.name == "Exchange":
                action_challenges.append(ActionChallenge(action, players[i]))
        return action_challenges

    class ActionChallenge(object):
        def __init__(self, action, challenger):
            self.action = action
            self.challenger = challenger
        def __repr__(self):
            return self.challenger.name + " " + "challenges " + "'" + self.action.__repr__() + "'"

    class Counteraction(object):
        def __init__(self, action, counteractor, claim):
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
                exchange(self.player, deck, success)

    def is_winner(players):
        in_players = 0
        for player in players:
            if check_player_in(player):
                in_players += 1
        if in_players == 1:
            return True
        return False

    deck = Deck()
    deck.shuffle()
    players = []
    num_players = 3
    for player_num in range(num_players):
        name = "Player " + str(player_num)
        players.append(Player(player_num, name))
        deck.deal(players[player_num], times=2)

    count = 0
    while not is_winner(players):

        actions = get_actions(count, players)
        action = random.choice(actions)
        print(actions)
        print(players[count].name + " plays '" + action.__repr__() + "' claiming " + action.action_character)

        action_challenges = get_action_challenges(action, players)
        action_challenge = random.choice(action_challenges)
        print(action_challenges)
        print(action_challenge)
        if not (action_challenge == None):
            winner, loser = challenge_action(action_challenge.action, action_challenge.challenger) # handle challenge
            if winner.id == action.player.id: # if the winner is the one who was challenged
                card_index = 0
                if winner.cards[1].name == action.action_character:
                    card_index = 1
                print(winner.name + " wins with " + winner.cards[card_index].name)
                action.execute(success=True)
                deck.append(winner.cards.pop(card_index))
                deck.shuffle()
                deck.deal(winner)
                loser.lose_influence() # The loser can choose which card to turn over
            else: # the winner is the one who challenged the action
                action.execute(success=False)
                print(winner.name + " wins!")
                loser.lose_influence() # Note: the loser has chosen a card to turn over to prove the challenge. Loser the same card that they chose to turn over
        else:
            counteractions = get_counteractions(players, action)
            print(counteractions)
            counteraction = random.choice(counteractions)
            print(counteraction)
            if counteraction == None: # the action went unchallenged so if no one counteracts the action succeeds 
                action.execute(success=True)
            else:
                if not (get_counteraction_challenges == None):
                    pass # handle challenge: if counteractor wins challenger loses influence 
                else:
                    pass


        break

if __name__ == "__main__":
    main()