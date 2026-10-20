#!/usr/bin/env bash

INTERVAL_SECONDS=10
LOG_FILE="monitor.log"

while true; do
  echo "--- $(date '+%Y-%m-%d %H:%M:%S') ---" >> "$LOG_FILE"
  free -h >> "$LOG_FILE"
  df -h >> "$LOG_FILE"
  uptime >> "$LOG_FILE"
  sleep "$INTERVAL_SECONDS"
done
