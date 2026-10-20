#!/usr/bin/env bash
set -eu

# Интервал является константой задания; интерактивный ввод не используется.
INTERVAL_SECONDS=10
LOG_FILE="${MONITOR_LOG:-monitor.log}"

for required_command in date free df uptime sleep; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'Ошибка: команда %s не найдена.\n' "$required_command" >&2
    exit 1
  fi
done

if ! touch "$LOG_FILE" 2>/dev/null; then
  printf 'Ошибка: невозможно записать в %s.\n' "$LOG_FILE" >&2
  exit 1
fi

printf 'Мониторинг запущен: интервал %s с, журнал %s. Для остановки нажмите Ctrl+C.\n' \
  "$INTERVAL_SECONDS" "$LOG_FILE"
trap 'printf "\nМониторинг остановлен.\n"; exit 0' INT TERM

sample_count=0
while true; do
  {
    printf '%s\n' "--- $(date '+%Y-%m-%d %H:%M:%S') ---"
    free -h
    df -h
    uptime
    printf '\n'
  } >>"$LOG_FILE"

  sample_count=$((sample_count + 1))
  # Служебный режим нужен только для автоматической проверки и примера вывода.
  if [ "${MONITOR_ONCE:-0}" = "1" ] && [ "$sample_count" -ge 1 ]; then
    break
  fi
  sleep "$INTERVAL_SECONDS"
done
