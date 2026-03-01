#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting FlipMeOver installation (Standard macOS Edition)...${NC}"

CURRENT_USER=$(whoami)
SCRIPT_DIR=$(pwd)
PLIST_NAME="com.$CURRENT_USER.flipmeover"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
LOG_DIR="$HOME/Library/Logs/FlipMeOver"

echo -e "${GREEN}Setting up virtual environment with native Python...${NC}"
mkdir -p "$LOG_DIR"

if command -v python3 &> /dev/null
then
    python3 -m venv .venv
    source .venv/bin/activate

    echo -e "${GREEN}Installing required macOS framework (PyObjC)...${NC}"
    pip install --upgrade pip
    pip install pyobjc-framework-Cocoa
else
    echo -e "${RED}Error: Python 3 not found.${NC}"
    echo "Please install Python 3 or Command Line Tools (xcode-select --install)."
    exit 1
fi

echo -e "${GREEN}Configuring LaunchAgent...${NC}"

cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/.venv/bin/python3</string>
        <string>$SCRIPT_DIR/flip_me_over.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/launchagent.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/launchagent.log</string>
</dict>
</plist>
EOF

echo -e "${GREEN}Loading FlipMeOver into system background services...${NC}"
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}SUCCESS! FlipMeOver is now running.${NC}"
echo -e "Your Magic Mouse is now being monitored."
echo -e "The app will start automatically at every login."
echo -e "${BLUE}=======================================${NC}"