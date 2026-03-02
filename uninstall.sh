#!/bin/bash

APP_NAME="FlipMeOver"
INSTALL_DIR="$HOME/Library/Application Support/$APP_NAME"
LOG_DIR="$HOME/Library/Logs/$APP_NAME"
PLIST_LABEL="com.user.flipmeover"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"

echo "🗑️ Uninstalling $APP_NAME..."

if [ -f "$PLIST_PATH" ]; then
    echo "🔌 Stopping background service..."
    launchctl unload "$PLIST_PATH"
    rm "$PLIST_PATH"
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "📦 Removing application files..."
    rm -rf "$INSTALL_DIR"
fi

echo "📄 Cleaning up logs..."
rm -rf "$LOG_DIR"

echo "✅ $APP_NAME has been successfully uninstalled."