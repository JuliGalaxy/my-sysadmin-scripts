#!/usr/bin/env bash
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Запустите скрипт через sudo." >&2
  exit 1
fi

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

systemctl enable --now docker
docker build -t my-script:latest "$REPO_DIR"

if docker container inspect my-app >/dev/null 2>&1; then
  docker rm -f my-app
fi
docker create \
  --name my-app \
  --publish 127.0.0.1:8080:8080 \
  --volume /mnt/logs:/var/www \
  my-script:latest

install -D -m 0644 "$REPO_DIR/systemd/my-app.service" /etc/systemd/system/my-app.service
install -D -m 0644 "$REPO_DIR/nginx/my-app.conf" /etc/nginx/conf.d/my-app.conf

mkdir -p /etc/ssl/private /etc/ssl/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/my-app.key \
  -out /etc/ssl/certs/my-app.crt \
  -subj "/CN=my-app.local"
chmod 0600 /etc/ssl/private/my-app.key

systemctl daemon-reload
systemctl enable --now my-app
sleep 3
nginx -t
systemctl enable --now nginx
systemctl reload nginx

curl --fail --silent --show-error http://127.0.0.1:8080/monitor.log >/dev/null
curl --fail --insecure --silent --show-error https://127.0.0.1/monitor.log >/dev/null

echo "Сервис развёрнут: https://$(hostname -I | awk '{print $1}')/monitor.log"
