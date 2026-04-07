#!/usr/bin/env bash
# Installs plugin.video.onedriveshare into ~/.kodi/addons (desktop Linux / macOS Kodi).
# For Android TV, copy the plugin folder with adb or use the zip from the setup page.
set -euo pipefail
BASE="${BASE:-https://raw.githubusercontent.com/ghemed/kodi-setup/main/plugin.video.onedriveshare}"
ROOT="${HOME}/.kodi/addons/plugin.video.onedriveshare"
paths=(
  addon.xml
  addon.py
  resources/settings.xml
  resources/__init__.py
  resources/lib/__init__.py
  resources/lib/config.py
)
echo "Installing OneDrive Share addon to: $ROOT"
for p in "${paths[@]}"; do
  mkdir -p "$(dirname "$ROOT/$p")"
  curl -fsSL "$BASE/$p" -o "$ROOT/$p"
done
echo "Done. Restart Kodi, then open Add-ons -> Video add-ons -> OneDrive Share."
