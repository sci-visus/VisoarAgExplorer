#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/VisoarAgExplorer.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/VisoarAgExplorer.dmg" && rm "dist/VisoarAgExplorer.dmg"
create-dmg \
  --volname "VisoarAgExplorer" \
  --volicon "icons/visoareye.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "VisoarAgExplorer.app" 175 120 \
  --hide-extension "VisoarAgExplorer.app" \
  --app-drop-link 425 120 \
  "dist/VisoarAgExplorer.dmg" \
  "dist/dmg/"
