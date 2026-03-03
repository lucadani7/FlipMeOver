#!/bin/bash

APP_NAME="FlipMeOver"
INSTALL_DIR="$HOME/Library/Application Support/$APP_NAME"
LOG_DIR="$HOME/Library/Logs/$APP_NAME"
PLIST_LABEL="com.user.flipmeover"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

echo "🚀 Starting installation of $APP_NAME for user: $USER"

mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"

echo "📦 Copying files to $INSTALL_DIR..."
cp mouse_monitor.py "$INSTALL_DIR/"
cp flip_me_over.py "$INSTALL_DIR/"

echo "🛠️ Setting up Python environment..."
cd "$INSTALL_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pyobjc-framework-Cocoa pyobjc-framework-IOBluetooth

echo "📝 Registering LaunchAgent..."
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/.venv/bin/python</string>
        <string>$INSTALL_DIR/flip_me_over.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/service.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/service.log</string>
</dict>
</plist>
EOF

echo "🔌 Starting background service..."
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "✅ Installation complete!"
echo "✨ $APP_NAME will now start automatically at login."