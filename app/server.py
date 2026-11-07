import json
import os
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from .engine import DEFAULT_SETTINGS, SPORTS, demo_games, choose_game
from .playback import SimulatedPlaybackAdapter

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = Path(os.environ.get('GAMESWITCH_SETTINGS', str(Path.home() / '.gameswitch-settings.json')))
state_lock = threading.RLock()
settings = dict(DEFAULT_SETTINGS)
try:
    saved = json.loads(SETTINGS_PATH.read_text())
    if isinstance(saved, dict):
        settings.update(saved)
except (FileNotFoundError, ValueError, OSError):
    pass
state = {'current_id': None, 'last_switch': 0, 'tick': 0, 'last_result': None, 'events': []}
adapter = SimulatedPlaybackAdapter()

def snapshot():
    with state_lock:
        games = demo_games(state['tick'])
        selected, ranked, reason = choose_game(games, settings, state['current_id'], state['last_switch'], time.monotonic())
        if settings.get('auto_mode') and selected != state['current_id'] and selected is not None:
            selected_game = next(g for g in games if g.id == selected)
            state['current_id'] = selected
            state['last_switch'] = time.monotonic()
            state['last_result'] = adapter.select(selected_game.serialize())
            state['events'].insert(0, {'at': time.strftime('%H:%M:%S'), 'game': selected_game.home + ' vs ' + selected_game.away, 'reason': reason})
            state['events'] = state['events'][:15]
        return {'games': ranked, 'current_id': state['current_id'], 'reason': reason, 'settings': settings,
                'playback': state['last_result'], 'events': state['events'], 'tick': state['tick']}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'static'), **kwargs)

    def send_json(self, payload, status=200):
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if urlparse(self.path).path == '/api/state':
            self.send_json(snapshot())
        else:
            super().do_GET()

    def do_POST(self):
        route = urlparse(self.path).path
        if route not in {'/api/settings', '/api/advance', '/api/select'}:
            return self.send_json({'error': 'Not found'}, 404)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size > 65536:
                return self.send_json({'error': 'Request too large'}, 413)
            body = json.loads(self.rfile.read(size) or b'{}')
            if not isinstance(body, dict):
                raise ValueError('Expected object')
            with state_lock:
                if route == '/api/settings':
                    if 'favorite_teams' in body:
                        if not isinstance(body['favorite_teams'], list) or not all(isinstance(t, str) for t in body['favorite_teams']):
                            raise ValueError('favorite_teams must be a list of strings')
                        settings['favorite_teams'] = [t.strip()[:80] for t in body['favorite_teams'][:30] if t.strip()]
                    if 'sports' in body:
                        if not isinstance(body['sports'], list) or not all(isinstance(s, str) and s in SPORTS for s in body['sports']):
                            raise ValueError('Unknown sports')
                        settings['sports'] = list(dict.fromkeys(body['sports']))
                    for key in ('auto_mode', 'favorite_first', 'aggressive_switching'):
                        if key in body:
                            if not isinstance(body[key], bool):
                                raise ValueError(f'{key} must be boolean')
                            settings[key] = body[key]
                    if 'min_seconds_between_switches' in body:
                        n = body['min_seconds_between_switches']
                        if not isinstance(n, int) or not 0 <= n <= 3600:
                            raise ValueError('Invalid cooldown')
                        settings['min_seconds_between_switches'] = n
                    SETTINGS_PATH.write_text(json.dumps(settings, indent=2))
                elif route == '/api/advance':
                    state['tick'] += 1
                elif route == '/api/select':
                    game_id = body.get('id')
                    game = next((g for g in demo_games(state['tick']) if g.id == game_id), None)
                    if not game:
                        raise ValueError('Unknown game')
                    state['current_id'] = game.id
                    state['last_switch'] = time.monotonic()
                    state['last_result'] = adapter.select(game.serialize())
                    state['events'].insert(0, {'at': time.strftime('%H:%M:%S'), 'game': game.home + ' vs ' + game.away, 'reason': 'Manual selection'})
            self.send_json(snapshot())
        except (ValueError, TypeError, OSError) as exc:
            self.send_json({'error': str(exc)}, 400)

def main():
    host = os.environ.get('GAMESWITCH_HOST', '127.0.0.1')
    port = int(os.environ.get('GAMESWITCH_PORT', '8765'))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f'GameSwitch running at http://{host}:{port}', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()
