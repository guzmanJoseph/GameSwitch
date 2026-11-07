#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
python3 -m app.server &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 1
open -a 'Google Chrome' 'http://127.0.0.1:8765' 2>/dev/null || open 'http://127.0.0.1:8765'
wait "$SERVER_PID"
