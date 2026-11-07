import unittest
from app.engine import DEFAULT_SETTINGS, demo_games, score_game, choose_game

class EngineTests(unittest.TestCase):
    def test_favorite_priority(self):
        games=demo_games(0)
        self.assertGreater(score_game(games[0], DEFAULT_SETTINGS), score_game(games[1], DEFAULT_SETTINGS))
    def test_excluded_sport(self):
        settings={**DEFAULT_SETTINGS,'sports':['nfl']}
        self.assertEqual(score_game(demo_games(0)[0], settings), -10000)
    def test_selection(self):
        game_id, ranked, reason=choose_game(demo_games(0), DEFAULT_SETTINGS, None, 0, 100)
        self.assertEqual(game_id, ranked[0]['game']['id'])
    def test_cooldown(self):
        settings={**DEFAULT_SETTINGS,'favorite_teams':['Miami Heat'],'min_seconds_between_switches':30}
        selected,_,_=choose_game(demo_games(0),settings,'nfl',95,100)
        self.assertEqual(selected,'nfl')
if __name__=='__main__':unittest.main()
