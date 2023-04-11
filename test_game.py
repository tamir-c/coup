import unittest

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
    def test_two_player_coins(self):
        p = Player(0, 2)
        self.assertEqual(p.coins, 1)
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
        self.deck = Deck()
        self.p1 = Player(0, 2)
        self.p2 = Player(0, 2)
        self.deck.deal(self.p1, 2)
        self.deck.deal(self.p2, 2)
    def test_check_player_in(self):
        self.assertTrue(check_player_in(self.p1))
        self.p1.cards[0].showing = True
        self.p1.cards[1].showing = True
        self.assertFalse(check_player_in(self.p1)) 
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
        actions = get_actions(self.p1, [self.p1, self.p2], self.deck)
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
        actions = get_actions(self.p1, [self.p1, self.p2], self.deck)
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
        actions = get_actions(self.p1, [self.p1, self.p2], self.deck)
        names = [action.name for action in actions]
        self.assertIn("Coup", names)
        self.assertEqual(len(actions), 1)
    def test_get_actions_4(self):
        self.p2.coins = 0
        actions = get_actions(self.p1, [self.p1, self.p2], self.deck)
        names = [action.name for action in actions]
        self.assertNotIn("Steal", names)
    
class TestActions(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()
        self.p1 = Player(0, 3)
        self.p2 = Player(0, 3)
        self.deck.deal(self.p1, 2)
        self.deck.deal(self.p2, 2)
    def test_income_1(self):
        c = self.p1.coins
        income(self.p1, True)
        self.assertEqual(self.p1.coins, c+1)
    def test_income_2(self):
        c = self.p1.coins
        income(self.p1, False)
        self.assertNotEqual(self.p1.coins, c+1)
    def test_foreign_aid_1(self):
        c = self.p1.coins
        foreign_aid(self.p1, True)
        self.assertEqual(self.p1.coins, c+2)
    def test_foreign_aid_2(self):
        c = self.p1.coins
        foreign_aid(self.p1, False)
        self.assertNotEqual(self.p1.coins, c+2)
    def test_coup(self):
        self.p1.coins = 7
        coup(self.p1, self.p2, True)
        self.assertEqual(self.p1.coins, 0)
        self.assertEqual(self.p2.num_influences(), 1)

if __name__ == '__main__':
    unittest.main()