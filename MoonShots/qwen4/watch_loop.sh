#!/bin/sh
# Qwen 4 watcher loop (MoonShots): one read-only pass every 5 minutes until a hit (watch.py exits 2), then stop.
# Network errors are logged and retried next pass. Run in the background; it costs no session turns until it fires.
cd "$(dirname "$0")" || exit 1
while true; do
  python3 watch.py --once
  rc=$?
  if [ "$rc" -eq 2 ]; then echo "HIT: see qwen4/FOUND.json"; exit 0; fi
  if [ "$rc" -ne 0 ]; then echo "$(date '+%F %T') watch.py failed (rc $rc), retrying in 5 min" >> watch.log; fi
  sleep 300
done
