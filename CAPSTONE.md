# Отчёт по ДЗ №2

Дата проверки: 21 октября 2026 года. Хост: `10.0.19.113`, RED OS 7.3.5.

## Часть 1 — контейнер и хранилище

Образ `my-script:latest` собран из `ubuntu:22.04`. Контейнер запускает мониторинг ресурсов и HTTP-сервер на порту 8080. Каталог `/mnt/logs`, расположенный на LVM-томе, подключён в контейнер как `/var/www`, поэтому `monitor.log` сохраняется вне контейнера.

Проверка контейнера:

```text
$ docker ps --filter name=my-app
name=my-app status=Up (healthy) ports=127.0.0.1:8080->8080/tcp

$ curl -I http://127.0.0.1:8080/monitor.log
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.10.12
```

RAID 1 собран на двух loop-устройствах:

```text
$ cat /proc/mdstat
Personalities : [raid1]
md0 : active raid1 loop1[1] loop0[0]
      523264 blocks super 1.2 [2/2] [UU]
```

Дополнительно создан LVM-том:

```text
$ sudo lvs
LV       VG       Attr       LSize
lv_logs  vg_data  -wi-ao---- 200.00m

$ df -h /mnt/raid /mnt/logs
Filesystem                   Size  Used Avail Use% Mounted on
/dev/md0                     485M   14K  456M   1% /mnt/raid
/dev/mapper/vg_data-lv_logs  189M   27K  175M   1% /mnt/logs
```

## Часть 2 — Nginx, TLS и systemd

Nginx принимает внешние подключения. HTTP перенаправляется на HTTPS, а HTTPS проксируется на контейнер, доступный хосту по `127.0.0.1:8080`.

```text
$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

$ curl -I http://10.0.19.113/monitor.log
HTTP/1.1 301 Moved Permanently
Server: nginx/1.30.4

$ curl -kI https://10.0.19.113/monitor.log
HTTP/1.1 200 OK
Server: nginx/1.30.4
```

Проверка с отдельной Windows-машины также вернула `HTTP/1.1 200 OK`.

Контейнер управляется systemd:

```text
$ systemctl is-active my-app
active
$ systemctl is-enabled my-app
enabled
```

После HTTPS-запроса запись появилась и в `journalctl -u my-app`, и в `/var/log/nginx/access.log`.

## Воспроизведение

Полный стенд можно развернуть без интерактивного ввода:

```bash
sudo ./bootstrap.sh
```

Скрипт автоматически устанавливает зависимости, создаёт RAID 1 и LVM, собирает Docker-образ, создаёт self-signed сертификат, устанавливает конфигурацию Nginx и включает systemd-службы.

## Что показать на защите

1. `docker ps` и `curl http://127.0.0.1:8080/monitor.log`.
2. `cat /proc/mdstat`, `sudo lvs` и `df -h /mnt/raid /mnt/logs`.
3. `sudo nginx -t` и `curl -kI https://10.0.19.113/monitor.log`.
4. `systemctl status my-app` и `sudo journalctl -u my-app -n 10 --no-pager`.
