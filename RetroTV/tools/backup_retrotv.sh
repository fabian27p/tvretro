#!/usr/bin/env bash
set -euo pipefail
BASE="${RETROTV_BASE:-/home/retro/RetroTV}"; MODE="${1:---without-videos}"; STAMP=$(date +%Y%m%d-%H%M%S); DEST="$BASE/backups/retrotv-$STAMP.tar.gz"; mkdir -p "$BASE/backups"
case "$MODE" in
 --config-only) tar -czf "$DEST" -C "$BASE" config app systemd tools;;
 --without-videos) tar --exclude='channels/*/*' -czf "$DEST" -C "$BASE" app assets config systemd tools logs;;
 --full) tar -czf "$DEST" -C "$BASE" app assets channels config systemd tools logs;;
 *) echo "Uso: $0 --config-only|--without-videos|--full"; exit 1;;
esac
echo "$DEST"
