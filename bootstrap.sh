#!/usr/bin/env bash
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Запустите: sudo ./bootstrap.sh" >&2
  exit 1
fi

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io nginx mdadm lvm2 openssl curl
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y docker nginx mdadm lvm2 openssl curl
else
  echo "Поддерживаются системы с apt-get или dnf." >&2
  exit 1
fi

chmod +x "$REPO_DIR/storage-setup.sh" "$REPO_DIR/deploy.sh" "$REPO_DIR/script.sh"
"$REPO_DIR/storage-setup.sh"
"$REPO_DIR/deploy.sh"
