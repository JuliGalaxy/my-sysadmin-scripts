# My Sysadmin Scripts

Учебный капстоун: мониторинг ресурсов в Docker-контейнере, RAID 1 и LVM на loop-устройствах, Nginx reverse proxy с TLS и управление контейнером через systemd.

## Быстрый запуск

На Ubuntu, Debian, RED OS или Fedora весь стенд разворачивается одной командой:

```bash
sudo ./bootstrap.sh
```

Скрипт создаёт RAID 1 в `/mnt/raid`, LVM-том в `/mnt/logs`, собирает образ `my-script`, запускает контейнер `my-app`, устанавливает self-signed сертификат и публикует сервис через HTTPS.

## Проверка

```bash
docker ps
curl http://127.0.0.1:8080/monitor.log
sudo nginx -t
curl -kI https://127.0.0.1/monitor.log
systemctl status my-app
cat /proc/mdstat
sudo lvs
df -h /mnt/raid /mnt/logs
```

Self-signed сертификат предназначен только для учебной среды, поэтому при проверке `curl` используется флаг `-k`.

## Материалы итоговой защиты

- [Итоговый PDF-отчёт](docs/Итоговый_отчет_капстоун.pdf)
- [Текстовый отчёт и команды проверки](CAPSTONE.md)
- [Исходные скриншоты ДЗ №1](1/)
- [Исходные скриншоты ДЗ №2 и итоговой проверки](2/)

Подготовленные фрагменты скриншотов, использованные в PDF, находятся в [`docs/evidence`](docs/evidence/).
