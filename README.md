# GameSwitch MVP 1.0

Free, local-first sports game-ranking and **simulated** playback system. Runs on macOS with Python 3.10+ using only the standard library: no paid hosting, sports API, subscription, or Node required.

## Quick start

```bash
git clone https://github.com/guzmanJoseph/GameSwitch.git
cd GameSwitch
python3 -m unittest discover -s tests -v
python3 -m app.server
```

Open **http://127.0.0.1:8765** in your browser. Use **Enter fullscreen** for a clean TV-friendly dashboard. To show it on Roku or Vizio TV, connect the Mac by HDMI and choose that HDMI input.

## What works

- Six simulated sports: CFB, NFL, soccer, NBA, MLB, college basketball
- Favorite-team-first scoring, automatic selection, aggressive switching and configurable cooldown
- Minimalist fullscreen dashboard and decision log
- Settings saved locally in `~/.gameswitch-settings.json`
- Playback adapter architecture with explicit simulation and unsupported YouTube TV adapter
- Unit tests

Click **Simulate next game update** three or more times to cycle score scenarios. Set cooldown to `0` to test immediate decisions. Manual selection changes the simulated choice only.

## Auto-start on Mac

After testing, run:

```bash
chmod +x scripts/*.sh
./scripts/install-login-item-mac.sh
```

This adds a macOS login agent. It does not turn on the TV or bypass macOS login.

## Files

- `app/engine.py` — game ranking and simulation
- `app/playback.py` — playback adapter interfaces
- `app/server.py` — HTTP server and API
- `static/` — dashboard HTML, CSS and JavaScript
- `scripts/` — Mac launch helpers
- `tests/` — unit tests

## Budget

**$0 in new software costs.** Use your existing Mac and TV; only buy an HDMI cable/adapter if you don't already have one. No mini PC needed for the MVP. Investigate free, permitted live-score sources before considering paid APIs.

## Important limits

This version **does not play or control YouTube TV, detect commercials, or retrieve real scores**. Automatic live-channel selection has no verified general-purpose public YouTube TV API. Do not assume that Roku remote-control or browser automation can select specific live programs. Ad avoidance may violate service terms. Test supported integrations separately before buying hardware.

The local server binds to `127.0.0.1` by default. Do not expose its unauthenticated API to the internet.
