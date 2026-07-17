#!/usr/bin/env bash
set -euo pipefail
BASE="${RETROTV_BASE:-/home/retro/RetroTV}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OWNER="${SUDO_USER:-retro}"
sudo apt update
sudo apt install -y mpv python3 python3-gpiozero jq rsync
mkdir -p "$BASE"/{app,assets/{animations,sounds,images,fonts},channels,config,logs,backups,tools,systemd}
for n in $(seq -w 1 12); do mkdir -p "$BASE/channels/channel$n"; done
if [ "$SRC" != "$BASE" ]; then
  rsync -a --exclude='logs/' --exclude='backups/' --exclude='channels/channel*/**/*' "$SRC"/ "$BASE"/
fi
sudo chown -R "$OWNER:$OWNER" "$BASE"
sudo cp "$BASE/systemd/retrotv.service" /etc/systemd/system/retrotv.service
sudo systemctl daemon-reload
echo "Listo. Prueba: python3 $BASE/app/main.py"
