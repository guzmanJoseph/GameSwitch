from dataclasses import dataclass, asdict
from typing import Optional

SPORTS = ['cfb', 'nfl', 'soccer', 'nba', 'mlb', 'cbb']
DEFAULT_SETTINGS = {
    'sports': SPORTS,
    'favorite_teams': ['Florida Gators'],
    'favorite_first': True,
    'aggressive_switching': True,
    'switch_threshold': 5,
    'min_seconds_between_switches': 20,
    'auto_mode': True,
}

@dataclass
class Game:
    id: str
    sport: str
    home: str
    away: str
    home_score: int
    away_score: int
    period: str
    clock: str
    status: str = 'live'
    importance: int = 0
    channel: str = 'Demo Channel'

    def serialize(self):
        return asdict(self)

def score_game(game: Game, settings: dict) -> int:
    if game.status != 'live' or game.sport not in settings.get('sports', SPORTS):
        return -10000
    favorites = {s.casefold().strip() for s in settings.get('favorite_teams', [])}
    favorite = game.home.casefold().strip() in favorites or game.away.casefold().strip() in favorites
    margin = abs(game.home_score - game.away_score)
    closeness = max(0, 50 - margin * 4)
    late = 20 if game.period.lower() in {'q4', '2h', '9th', 'ot', 'extra time'} else 0
    favorite_points = 200 if settings.get('favorite_first', True) and favorite else (70 if favorite else 0)
    return favorite_points + closeness + late + game.importance

def choose_game(games: list[Game], settings: dict, current_id: Optional[str], last_switch: float, now: float):
    ranked = sorted(({'game': g.serialize(), 'score': score_game(g, settings)} for g in games), key=lambda x: x['score'], reverse=True)
    ranked = [r for r in ranked if r['score'] > -10000]
    if not ranked:
        return None, ranked, 'No eligible live games'
    best = ranked[0]
    current = next((r for r in ranked if r['game']['id'] == current_id), None)
    if not current:
        return best['game']['id'], ranked, 'Selected highest-ranked live game'
    if best['game']['id'] == current_id:
        return current_id, ranked, 'Current game remains the best choice'
    if now - last_switch < settings.get('min_seconds_between_switches', 20):
        return current_id, ranked, 'Switch cooldown active'
    if best['score'] - current['score'] < settings.get('switch_threshold', 5):
        return current_id, ranked, 'New game does not exceed switching threshold'
    return best['game']['id'], ranked, 'Switched to higher-ranked game'

def demo_games(tick: int) -> list[Game]:
    phase = (tick // 3) % 4
    return [
        Game('gators', 'cfb', 'Florida Gators', 'Georgia Bulldogs', 24, [21, 31, 28, 24][phase], 'Q4', '02:14', importance=25, channel='Demo ESPN'),
        Game('nfl', 'nfl', 'Miami Dolphins', 'Buffalo Bills', 27, [27, 24, 17, 27][phase], 'Q4', '04:02', importance=35, channel='Demo CBS'),
        Game('nba', 'nba', 'Miami Heat', 'Boston Celtics', 103, [101, 120, 103, 104][phase], 'Q4', '01:32', importance=20, channel='Demo TNT'),
        Game('soccer', 'soccer', 'Inter Miami', 'Orlando City', 2, [2, 1, 3, 2][phase], '2H', '87:15', importance=20, channel='Demo FOX'),
        Game('mlb', 'mlb', 'New York Yankees', 'Boston Red Sox', 4, [4, 8, 5, 4][phase], '9th', 'Top 9', importance=15, channel='Demo FS1'),
        Game('cbb', 'cbb', 'Florida Gators', 'Kentucky Wildcats', 72, [70, 83, 72, 69][phase], '2H', '01:05', importance=15, channel='Demo ESPN2'),
    ]
