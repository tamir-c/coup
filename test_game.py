import unittest
from state import *
from game import *

class TestCard(unittest.TestCase):
    def test_card_names(self):
        c0 = Card(0)
        c1 = Card(1)
        c2 = Card(2)
        c3 = Card(3)
        c4 = Card(4)
        self.assertEqual(c0.name, "Duke")
        self.assertEqual(c1.name, "Assassin")
        self.assertEqual(c2.name, "Ambassador")
        self.assertEqual(c3.name, "Captain")
        self.assertEqual(c4.name, "Contessa")

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.p = Player(0, 3, agent=None)

    def test_player_init(self):
        self.assertEqual(self.p.agent.name, "Random Agent")
        self.assertEqual(self.p.id, 0)
        self.assertEqual(self.p.name, "Player 0")
        self.assertEqual(self.p.coins, 2)
    # def test_two_player_coins(self): # Two player variant not implemented currently
    #     p = Player(0, 2)
    #     self.assertEqual(p.coins, 1)
    def test_num_influences(self):
        d = Deck()
        d.deal(self.p, 2)
        self.assertEqual(self.p.num_influences(), 2)
        self.p.cards[0].showing = True
        self.assertEqual(self.p.num_influences(), 1)
        self.p.cards[1].showing = True
        self.assertEqual(self.p.num_influences(), 0)
    def test_get_active_cards(self):
        d = Deck()
        d.deal(self.p, 2)
        a = self.p.get_active_cards()
        self.assertEqual(len(a), 2)
        self.p.cards[0].showing = True
        a = self.p.get_active_cards()
        self.assertEqual(len(a), 1)
        self.p.cards[1].showing = True
        a = self.p.get_active_cards()
        self.assertEqual(len(a), 0)
    def test_get_active_action_characters(self):
        d = Deck()
        d.deal_character(self.p, 0)
        d.deal_character(self.p, 1)
        self.assertIn("Duke", self.p.get_active_action_characters())
        self.assertIn("Assassin", self.p.get_active_action_characters())
        self.p.cards[0].showing = True
        self.p.cards[1].showing = True
        self.assertNotIn("Duke", self.p.get_active_action_characters())
        self.assertNotIn("Assassin", self.p.get_active_action_characters())
    def test_repr(self):
        self.assertEqual(self.p.__repr__(), "Player 0")
    def test_lose_influence_1(self):
        d = Deck()
        d.deal_character(self.p, 0)
        d.deal_character(self.p, 1)
        self.assertFalse(self.p.cards[0].showing)
        self.assertFalse(self.p.cards[1].showing)
        self.p.lose_influence()
        self.assertTrue(self.p.cards[0].showing)
        self.assertFalse(self.p.cards[1].showing)
        self.p.lose_influence()
        self.assertTrue(self.p.cards[0].showing)
        self.assertTrue(self.p.cards[1].showing)
    def test_lose_influence_2(self):
        d = Deck()
        d.deal_character(self.p, 0)
        d.deal_character(self.p, 1)
        self.p.cards[1].showing = True
        self.assertFalse(self.p.cards[0].showing)
        self.assertTrue(self.p.cards[1].showing)
        self.p.lose_influence()
        self.assertTrue(self.p.cards[0].showing)

class TestDeck(unittest.TestCase):
    def setUp(self):
        self.d = Deck()

    def test_deck_setup(self):
        self.assertEqual(self.d[0].name, "Duke")
    def test_deal(self):
        p = Player(0, 3)
        self.d.deal(p)
        self.assertEqual(len(p.cards), 1)
        self.d.deal(p)
        self.assertEqual(len(p.cards), 2)
        self.assertEqual(p.cards[0].showing, False)
        self.assertEqual(p.cards[1].showing, False)
        self.d.deal(p)
        self.assertEqual(len(p.cards), 2)
    def test_deal_character(self):
        p = Player(0, 3)
        self.d.deal_character(p, 0)
        self.assertEqual(p.cards[0].name, "Duke")
        self.d.deal_character(p, 4)
        self.assertEqual(p.cards[1].name, "Contessa")
        self.d.deal_character(p, 4)
        self.assertEqual(len(p.cards), 2)
        self.assertEqual(len(self.d), 13)

class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.state = State(num_players=2)
        self.p1 = self.state.players[0]
        self.p2 = self.state.players[1]
    def test_check_player_in(self):
        self.assertTrue(self.p1.check_player_in())
        self.p1.cards[0].showing = True
        self.p1.cards[1].showing = True
        self.assertFalse(self.p1.check_player_in()) 
    def test_check_coup(self):
        self.assertFalse(check_coup(self.p1, self.p2))
        self.assertFalse(check_coup(self.p2, self.p1))
        self.p1.coins = 7
        self.assertTrue(check_coup(self.p1, self.p2))
        self.assertFalse(check_coup(self.p2, self.p1))
        self.p2.lose_influence()
        self.p2.lose_influence()
        self.assertFalse(check_coup(self.p1, self.p2))
    def test_check_assassinate(self):
        self.assertFalse(check_assassinate(self.p1, self.p2))
        self.p1.coins = 3
        self.p2.coins = 3
        self.assertTrue(check_assassinate(self.p1, self.p2))
        self.assertTrue(check_assassinate(self.p2, self.p1))
        self.p2.lose_influence()
        self.p2.lose_influence()
        self.assertFalse(check_assassinate(self.p1, self.p2))
    def test_check_steal(self):
        self.assertTrue(check_steal(self.p1, self.p2))
        self.assertTrue(check_steal(self.p2, self.p1))
        self.p1.coins = 0
        self.assertTrue(check_steal(self.p1, self.p2))
        self.assertFalse(check_steal(self.p2, self.p1))
        self.p1.lose_influence()
        self.p1.lose_influence()
        self.assertFalse(check_steal(self.p1, self.p2))
    def test_get_actions_1(self):
        actions = self.state.get_actions()
        names = [action.name for action in actions]
        self.assertIn("Income", names)
        self.assertIn("Foreign Aid", names)
        self.assertIn("Tax", names)
        self.assertIn("Exchange", names)
        self.assertIn("Steal", names)
        self.assertNotIn("Coup", names)
        self.assertNotIn("Assassinate", names)
    def test_get_actions_2(self):
        self.p1.coins = 7
        actions = self.state.get_actions()
        names = [action.name for action in actions]
        self.assertIn("Coup", names)
        self.assertIn("Income", names)
        self.assertIn("Foreign Aid", names)
        self.assertIn("Tax", names)
        self.assertIn("Exchange", names)
        self.assertIn("Steal", names)
        self.assertIn("Assassinate", names) 
    def test_get_actions_3(self):
        self.p1.coins = 10
        actions = actions = self.state.get_actions()
        names = [action.name for action in actions]
        self.assertIn("Coup", names)
        self.assertEqual(len(actions), 1)
    def test_get_actions_4(self):
        self.p2.coins = 0
        actions = actions = self.state.get_actions()
        names = [action.name for action in actions]
        self.assertNotIn("Steal", names)
    
class TestActions(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()
        self.p1 = Player(0, 2)
        self.p2 = Player(1, 2)
        self.deck.deal(self.p1, 2)
        self.deck.deal(self.p2, 2)
    def test_income_1(self):
        c = self.p1.coins
        income(self.p1, True)
        self.assertEqual(self.p1.coins, c+1)
    def test_income_2(self):
        c = self.p1.coins
        income(self.p1, False)
        self.assertEqual(self.p1.coins, c)
    def test_foreign_aid_1(self):
        c = self.p1.coins
        foreign_aid(self.p1, True)
        self.assertEqual(self.p1.coins, c+2)
    def test_foreign_aid_2(self):
        c = self.p1.coins
        foreign_aid(self.p1, False)
        self.assertEqual(self.p1.coins, c)
    def test_coup_1(self):
        self.p1.coins = 7
        coup(self.p1, self.p2, True)
        self.assertEqual(self.p1.coins, 0)
        self.assertEqual(self.p2.num_influences(), 1)
    def test_coup_2(self):
        self.p1.coins = 7
        coup(self.p1, self.p2, False)
        self.assertEqual(self.p1.coins, 7)
        self.assertEqual(self.p2.num_influences(), 2)
    def test_tax_1(self):
        c = self.p1.coins
        tax(self.p1, True)
        self.assertEqual(self.p1.coins, c+3)
    def test_tax_2(self):
        c = self.p1.coins
        tax(self.p1, False)
        self.assertEqual(self.p1.coins, c)
    def test_assassinate_1(self):
        c = self.p1.coins
        assassinate(self.p1, self.p2, True)
        self.assertEqual(self.p1.coins, c-3)
        self.assertEqual(self.p2.num_influences(), 1)
    def test_assassinate_2(self):
        c = self.p1.coins
        assassinate(self.p1, self.p2, False)
        self.assertEqual(self.p1.coins, c-3)
        self.assertEqual(self.p2.num_influences(), 2)
    def test_steal_1(self):
        c = self.p2.coins
        steal(self.p1, self.p2, True)
        self.assertEqual(self.p2.coins, c-2)
    def test_steal_2(self):
        c = self.p2.coins
        steal(self.p1, self.p2, False)
        self.assertEqual(self.p2.coins, c)
    def test_steal_3(self):
        self.p2.coins = 1
        steal(self.p1, self.p2, True)
        self.assertEqual(self.p2.coins, 0)

class TestChallenges(unittest.TestCase):
    def setUp(self):
        self.state = State(num_players=2)
        self.state.deck.append(self.state.players[0].cards.pop())
        self.state.deck.append(self.state.players[0].cards.pop())
        self.state.deck.append(self.state.players[1].cards.pop())
        self.state.deck.append(self.state.players[1].cards.pop())
        self.state.deck.deal_character(self.state.players[0], 0) # deals duke
        self.state.deck.deal_character(self.state.players[0], 4)
        self.state.deck.deal_character(self.state.players[1], 1)
        self.state.deck.deal_character(self.state.players[1], 1)
        self.state.stage = 1
    def test_challenge_action_1(self):
        self.state.action = self.state.get_actions()[2] 
        winner, loser = challenge_action(self.state.action, self.state.players[1])
        self.assertEqual(winner, self.state.players[0])
        self.assertEqual(loser, self.state.players[1])
    def test_challenge_action_2(self):
        self.state.actor = 1
        self.state.action = self.state.get_actions()[2] 
        winner, loser = challenge_action(self.state.action, self.state.players[0])
        self.assertEqual(winner, self.state.players[0])
        self.assertEqual(loser, self.state.players[1])
    def test_challenge_action_3(self):
        self.state.action = self.state.get_actions()[2] 
        self.state.players[0].lose_influence()
        winner, loser = challenge_action(self.state.action, self.state.players[1])
        self.assertEqual(winner, self.state.players[1])
        self.assertEqual(loser, self.state.players[0])
class TestDecisionGetters(unittest.TestCase):
    def setUp(self):
        self.state = State(num_players=2)
    def test_error_if_actor_not_in(self):
        self.state.players[0].lose_influence()
        self.state.players[0].lose_influence()
        with self.assertRaises(Exception):
            self.state.get_actions()
    def test_get_actions_1(self):
        self.assertEqual(self.state.get_actions()[0].name, "Income")
        
        
if __name__ == '__main__':
    unittest.main()