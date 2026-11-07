#!/bin/zsh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$HOME/Library/LaunchAgents"
PLIST="$HOME/Library/LaunchAgents/com.gameswitch.local.plist"
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.gameswitch.local</string>
<key>ProgramArguments</key><array><string>/bin/zsh</string><string>${ROOT}/scripts/start-mac.sh</string></array>
<key>RunAtLoad</key><true/>
<key>StandardOutPath</key><string>/tmp/gameswitch.log</string>
<key>StandardErrorPath</key><string>/tmp/gameswitch-error.log</string>
</dict></plist>
PLIST
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed login agent. To remove: launchctl bootout gui/$(id -u) '$PLIST'; rm '$PLIST'"
