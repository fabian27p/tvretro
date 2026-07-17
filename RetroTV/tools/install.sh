#!/usr/bin/env bash
set -euo pipefail
BASE="${RETROTV_BASE:-/home/retro/RetroTV}"
sudo apt update
sudo apt install -y mpv python3 python3-gpiozero jq rsync
mkdir -p "$BASE"/{app,assets/{animations,sounds,images,fonts},channels,config,logs,backups,tools}
for n in $(seq -w 1 12); do mkdir -p "$BASE/channels/channel$n"; done
sudo chown -R "${SUDO_USER:-retro}:${SUDO_USER:-retro}" "$BASE"
sudo cp "$BASE/systemd/retrotv.service" /etc/systemd/system/retrotv.service
sudo systemctl daemon-reload
echo "Listo. Prueba: python3 $BASE/app/main.py"
