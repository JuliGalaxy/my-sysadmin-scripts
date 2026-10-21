#!/usr/bin/env python3
"""Build the capstone defence report as a polished A4 PDF."""

from __future__ import annotations

import os
from html import escape
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
OUTPUT = ROOT / "Итоговый_отчет_капстоун.pdf"
STUDENT_NAME = os.environ.get("CAPSTONE_STUDENT_NAME", "Ведина Юлия Алексеевна")
REPOSITORY = "https://github.com/JuliGalaxy/my-sysadmin-scripts"

NAVY = colors.HexColor("#12355B")
BLUE = colors.HexColor("#176B87")
CYAN = colors.HexColor("#43A6C6")
PALE = colors.HexColor("#EEF6F8")
INK = colors.HexColor("#202833")
MUTED = colors.HexColor("#5F6B76")
LINE = colors.HexColor("#CBD7DF")
CODE_BG = colors.HexColor("#F4F6F8")
GREEN = colors.HexColor("#167A4A")


def register_fonts() -> None:
    fonts = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Arial", fonts / "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", fonts / "arialbd.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Italic", fonts / "ariali.ttf"))
    pdfmetrics.registerFont(TTFont("Consolas", fonts / "consola.ttf"))


def crop(source: str, target: str, box: tuple[int, int, int, int]) -> None:
    dst = EVIDENCE / target
    with PILImage.open(EVIDENCE / source) as image:
        image.crop(box).save(dst, optimize=True)


def prepare_assets() -> None:
    with PILImage.open(EVIDENCE / "docker-build-original.png") as image:
        crop("docker-build-original.png", "docker-build.png", (0, 36, image.width, image.height))
    crop("nginx-tls.png", "nginx-check.png", (0, 0, 1439, 335))
    crop("nginx-tls.png", "tls-check.png", (0, 315, 1439, 620))
    crop("service-logs-original.png", "systemd-status.png", (0, 220, 1420, 535))
    crop("service-logs-original.png", "journal-log.png", (0, 500, 1836, 1005))
    crop("service-logs-original.png", "nginx-access-log.png", (0, 985, 1836, 1277))


register_fonts()
prepare_assets()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="BodyRU", parent=styles["BodyText"], fontName="Arial", fontSize=10.2,
    leading=14.3, textColor=INK, spaceAfter=7, alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="SmallRU", parent=styles["BodyRU"], fontSize=8.6, leading=11.2,
    textColor=MUTED, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="H1RU", parent=styles["Heading1"], fontName="Arial-Bold", fontSize=18,
    leading=22, textColor=NAVY, spaceBefore=2, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="H2RU", parent=styles["Heading2"], fontName="Arial-Bold", fontSize=13.2,
    leading=17, textColor=BLUE, spaceBefore=7, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="LabelRU", parent=styles["BodyRU"], fontName="Arial-Bold", fontSize=9.4,
    leading=12.5, textColor=NAVY, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="CaptionRU", parent=styles["SmallRU"], fontName="Arial-Italic", fontSize=8.2,
    leading=10.5, alignment=TA_CENTER, textColor=MUTED, spaceBefore=4, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="CoverTitle", parent=styles["Title"], fontName="Arial-Bold", fontSize=26,
    leading=31, alignment=TA_CENTER, textColor=NAVY, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="CoverSub", parent=styles["BodyRU"], fontName="Arial", fontSize=14,
    leading=20, alignment=TA_CENTER, textColor=BLUE,
))
styles.add(ParagraphStyle(
    name="Callout", parent=styles["BodyRU"], fontName="Arial", fontSize=9.4,
    leading=13, textColor=INK,
))


def p(text: str, style: str = "BodyRU") -> Paragraph:
    return Paragraph(text, styles[style])


def section(number: str, title: str, points: str) -> list:
    badge = Table(
        [[p(number, "LabelRU"), p(title, "H1RU"), p(points, "SmallRU")]],
        colWidths=[14 * mm, 132 * mm, 30 * mm],
        hAlign="LEFT",
    )
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (1, 0), (-1, 0), 1, LINE),
        ("ALIGN", (2, 0), (2, 0), "RIGHT"),
    ]))
    return [badge, Spacer(1, 5 * mm)]


def code(text: str) -> Table:
    safe = escape(text).replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;")
    paragraph = Paragraph(safe, ParagraphStyle(
        "CodeInline", fontName="Consolas", fontSize=7.7, leading=10.1,
        textColor=INK, wordWrap="CJK",
    ))
    box = Table([[paragraph]], colWidths=[174 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return box


def callout(label: str, text: str, color=PALE) -> Table:
    box = Table([[p(label, "LabelRU"), p(text, "Callout")]], colWidths=[30 * mm, 144 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return box


def figure(filename: str, caption: str, max_height_mm: float = 125) -> list:
    path = EVIDENCE / filename
    with PILImage.open(path) as img:
        width, height = img.size
    max_width = 174 * mm
    max_height = max_height_mm * mm
    scale = min(max_width / width, max_height / height)
    visual = Image(str(path), width=width * scale, height=height * scale)
    visual.hAlign = "CENTER"
    return [visual, p(caption, "CaptionRU")]


class ArchitectureDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 174 * mm
        self.height = 55 * mm

    def draw(self):
        c = self.canv
        nodes = [
            (0, "Клиент", "HTTPS :443"),
            (43.5, "Nginx", "TLS + proxy"),
            (87, "my-app", "127.0.0.1:8080"),
            (130.5, "LVM", "/mnt/logs"),
        ]
        for i, (xmm, title, sub) in enumerate(nodes):
            x = xmm * mm
            y = 21 * mm
            c.setFillColor(PALE if i else colors.HexColor("#E8F2FB"))
            c.setStrokeColor(BLUE)
            c.roundRect(x, y, 36 * mm, 21 * mm, 3 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont("Arial-Bold", 9)
            c.drawCentredString(x + 18 * mm, y + 12.5 * mm, title)
            c.setFont("Arial", 7.5)
            c.setFillColor(MUTED)
            c.drawCentredString(x + 18 * mm, y + 6.5 * mm, sub)
            if i < len(nodes) - 1:
                c.setStrokeColor(CYAN)
                c.setLineWidth(1.5)
                c.line(x + 36 * mm, y + 10.5 * mm, x + 42 * mm, y + 10.5 * mm)
                c.line(x + 40 * mm, y + 12.5 * mm, x + 42 * mm, y + 10.5 * mm)
                c.line(x + 40 * mm, y + 8.5 * mm, x + 42 * mm, y + 10.5 * mm)
        c.setFillColor(colors.HexColor("#F7F3E8"))
        c.setStrokeColor(colors.HexColor("#B79A42"))
        c.roundRect(50 * mm, 0, 74 * mm, 12 * mm, 2 * mm, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont("Arial", 8)
        c.drawCentredString(87 * mm, 4.5 * mm, "RAID 1: /dev/md0 → /mnt/raid (отдельный учебный слой)")


def page_frame(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 283 * mm, 192 * mm, 283 * mm)
        canvas.setFont("Arial", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 287 * mm, "Капстоун · Системное администрирование")
        canvas.drawRightString(192 * mm, 12 * mm, f"{doc.page}")
        canvas.drawString(18 * mm, 12 * mm, "Итоговый отчёт о защите")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
    topMargin=18 * mm, bottomMargin=18 * mm,
    title="Итоговый отчёт о защите капстоуна — Системное администрирование",
    author=STUDENT_NAME,
    subject="Доказательства выполнения технического чек-листа",
)

story = []

# Cover
story += [Spacer(1, 27 * mm)]
story += [p("ИТОГОВЫЙ ОТЧЁТ", "CoverSub"), Spacer(1, 5 * mm)]
story += [p("Защита капстоуна", "CoverTitle")]
story += [p("«Системное администрирование»", "CoverSub"), Spacer(1, 21 * mm)]
cover_data = [
    ["Студент", STUDENT_NAME],
    ["Дорожка", "Продвинутый"],
    ["Репозиторий", f'<link href="{REPOSITORY}" color="#176B87">{REPOSITORY}</link>'],
    ["Преподаватель", "Терещенко С. Н."],
    ["Среда", "RED OS 7.3.5 · 10.0.19.113"],
]
cover = Table(
    [[p(k, "LabelRU"), p(v, "BodyRU")] for k, v in cover_data],
    colWidths=[39 * mm, 121 * mm], hAlign="CENTER",
)
cover.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), PALE),
    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [cover, Spacer(1, 30 * mm)]
story += [p("2026", "CoverSub"), PageBreak()]

# Overview
story += [p("1. Краткое описание решения", "H1RU")]
story += [p(
    "На постоянном хосте RED OS 7.3.5 развёрнут единый воспроизводимый стенд. "
    "Скрипт варианта Б каждые 10 секунд записывает показатели памяти, дисков и нагрузки "
    "в <b>monitor.log</b>. Приложение работает в Docker-контейнере, управляется systemd "
    "и публикуется наружу только через Nginx с TLS. Команда <b>sudo ./bootstrap.sh</b> "
    "устанавливает зависимости и разворачивает все компоненты без интерактивного ввода."
)]
story += [Spacer(1, 4 * mm), ArchitectureDiagram(), Spacer(1, 4 * mm)]
summary_data = [
    ["Компонент", "Роль", "Результат"],
    ["script.sh", "Мониторинг ресурсов", "monitor.log"],
    ["Docker", "Изолированный запуск", "my-script:latest / my-app"],
    ["LVM", "Постоянное хранилище журнала", "vg_data/lv_logs → /mnt/logs"],
    ["RAID 1", "Демонстрация зеркалирования", "/dev/md0 → /mnt/raid"],
    ["Nginx + TLS", "Внешняя точка входа", "HTTPS 200, HTTP → HTTPS"],
    ["systemd", "Автозапуск и перезапуск", "enabled, active (running)"],
]
table = Table([[p(str(x), "SmallRU") for x in row] for row in summary_data], colWidths=[35 * mm, 68 * mm, 71 * mm], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.35, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [table, Spacer(1, 5 * mm)]
story += [callout("Итог", "Стенд проверен end-to-end: HTTPS-запрос проходит через Nginx в контейнер, возвращает файл с LVM-тома и фиксируется в обоих уровнях журналирования.")]
story += [PageBreak()]

# 1 Git
story += section("01", "Публичный Git-репозиторий", "4 балла")
story += [p("<b>Команда</b>")]
story += [code("git log --oneline -10")]
story += [Spacer(1, 3 * mm), p("<b>Результат</b>")]
story += [code("""cf4f7a3 docs: добавлен отчёт проверки капстоуна
c3dd838 fix: отключён стандартный HTTP-сайт RED OS
d0517ff fix: создание каталогов для TLS-сертификата
2c78ccb fix: учтён установленный Docker CE в RED OS
58514e5 feat: добавлено развёртывание с Nginx TLS и systemd
0070ab0 feat: добавлена настройка RAID 1 и LVM
22d9443 feat: контейнеризован мониторинг ресурсов
48be7a3 docs: добавлен README и пример вывода
26cf431 fix: добавлены проверки и корректная остановка
cfbe2fc draft: первая версия скрипта""")]
story += [Spacer(1, 4 * mm), callout("Что доказано", "Репозиторий содержит README и десять осмысленных коммитов. История показывает последовательное развитие решения: черновик, проверки, контейнеризация, хранилище, TLS/systemd и исправления под RED OS.")]
story += [Spacer(1, 5 * mm), p(
    f'<b>Публичная ссылка:</b> <link href="{REPOSITORY}" color="#176B87">{REPOSITORY}</link>'
)]
story += [PageBreak()]

# 2 Script
story += section("02", "Скрипт автоматизации", "4 балла")
story += [p("<b>Команда</b>")]
story += [code("sudo docker run --rm --entrypoint /bin/bash my-script -c '\n  MONITOR_ONCE=1 MONITOR_LOG=/tmp/monitor.log /usr/local/bin/script.sh;\n  head -20 /tmp/monitor.log'")]
story += [Spacer(1, 4 * mm)]
story += figure("script-run.png", "Рисунок 1 — Однократный контрольный запуск скрипта мониторинга внутри образа", 78)
story += [callout("Что доказано", "Скрипт варианта Б запускается без интерактивного ввода и формирует снимок с временной меткой, выводом free -h, df -h и uptime. Служебный режим MONITOR_ONCE используется только для воспроизводимой проверки.")]
story += [PageBreak()]

# 3 Docker
story += section("03", "Dockerfile, сборка и запуск контейнера", "4 балла")
story += [p("<b>Команды</b>")]
story += [code("sudo docker build --progress=plain -t my-script .\nsudo docker ps --filter name=my-app")]
story += [Spacer(1, 4 * mm)]
story += figure("docker-build.png", "Рисунок 2 — Успешная сборка образа my-script:latest из Dockerfile", 96)
story += figure("docker-ps.png", "Рисунок 3 — Контейнер my-app работает в состоянии healthy", 34)
story += [callout("Что доказано", "Dockerfile успешно собран, а контейнер my-app работает и прошёл healthcheck. Порт 8080 опубликован только на 127.0.0.1, поэтому прямой внешний доступ к приложению закрыт.")]
story += [PageBreak()]

# 4 Storage
story += section("04", "RAID 1 и LVM", "4 балла")
story += [p("<b>Команды</b>")]
story += [code("cat /proc/mdstat\nsudo lvs\ndf -h /mnt/raid /mnt/logs")]
story += [Spacer(1, 4 * mm)]
story += figure("storage.png", "Рисунок 4 — Состояние RAID 1, логического тома и точек монтирования", 95)
story += [callout("Что доказано", "Массив /dev/md0 собран как RAID 1 из двух loop-устройств; состояние [UU] подтверждает доступность обоих участников. Отдельно создан LVM-том vg_data/lv_logs; файловые системы смонтированы в /mnt/raid и /mnt/logs.")]
story += [PageBreak()]

# 5 Nginx
story += section("05", "Nginx как обратный прокси", "4 балла")
story += [p("<b>Команды</b>")]
story += [code("sudo nginx -t\ncurl -I http://10.0.19.113/monitor.log")]
story += [Spacer(1, 4 * mm)]
story += figure("nginx-check.png", "Рисунок 5 — Проверка конфигурации Nginx и перенаправление HTTP → HTTPS", 78)
story += [callout("Что доказано", "Проверка конфигурации завершилась сообщениями syntax is ok и test is successful. HTTP-запрос получает код 301 и перенаправляется на HTTPS; Nginx выступает единственной внешней точкой входа.")]
story += [PageBreak()]

# 6 TLS
story += section("06", "TLS и доступ по HTTPS", "4 балла")
story += [p("<b>Команда</b>")]
story += [code("curl -kI https://10.0.19.113/monitor.log")]
story += [Spacer(1, 4 * mm)]
story += figure("tls-check.png", "Рисунок 6 — Успешный HTTPS-запрос к опубликованному сервису", 82)
story += [callout("Что доказано", "Ответ HTTP/1.1 200 OK подтверждает, что TLS-блок активен, сертификат подключён и Nginx успешно передаёт запрос контейнеру. Флаг -k ожидаем для самоподписанного сертификата учебного стенда.")]
story += [PageBreak()]

# 7 systemd
story += section("07", "Управление контейнером через systemd", "3 балла")
story += [p("<b>Команда</b>")]
story += [code("systemctl status my-app --no-pager")]
story += [Spacer(1, 4 * mm)]
story += figure("systemd-status.png", "Рисунок 7 — Служба my-app включена и находится в состоянии active (running)", 78)
story += [callout("Что доказано", "Юнит my-app.service загружен, включён в автозапуск (enabled) и активен. В cgroup службы виден процесс docker start -a my-app; зависимости Requires/After задают запуск после Docker.")]
story += [Spacer(1, 4 * mm), p(
    "Примечание: <b>vendor preset: disabled</b> описывает политику пакета по умолчанию и не отменяет фактическое состояние <b>enabled</b>."
, "SmallRU")]
story += [PageBreak()]

# 8 logs
story += section("08", "Журналы systemd и Nginx", "3 балла")
story += [p("<b>Команды</b>")]
story += [code("sudo journalctl -u my-app -n 10 --no-pager\nsudo tail -5 /var/log/nginx/access.log")]
story += [Spacer(1, 4 * mm)]
story += figure("journal-log.png", "Рисунок 8 — Запросы к monitor.log в журнале службы my-app", 66)
story += figure("nginx-access-log.png", "Рисунок 9 — Тот же контрольный запрос с кодом 200 в access.log Nginx", 48)
story += [callout("Что доказано", "После контрольного HTTPS-запроса обращение к /monitor.log с кодом 200 видно в journalctl и access.log. Это подтверждает полный маршрут запроса Nginx → контейнер и работоспособность обоих уровней журналирования.")]
story += [PageBreak()]

# Architecture decisions
story += [p("2. Архитектурные решения", "H1RU")]
story += [p("2.1 Почему выбран вариант Б", "H2RU")]
story += [p(
    "Выбран вариант <b>Б — мониторинг ресурсов</b>. Он формирует полезный непрерывно обновляемый "
    "артефакт monitor.log, не требует интерактивного ввода и естественно переносится в контейнер. "
    "Вариант А сильнее зависит от журналов и прав хостовой системы и потребовал бы отдельного "
    "read-only-монтирования. Вариант В предназначен для изменения учётных записей и хуже подходит "
    "для демонстрации постоянно работающего сетевого сервиса."
)]
story += [p("2.2 RAID 1 и LVM решают разные задачи", "H2RU")]
story += [p(
    "RAID 1 дублирует данные на двух устройствах и повышает отказоустойчивость ценой половины "
    "суммарной ёмкости. LVM создаёт абстракцию над блочными устройствами и упрощает управление "
    "логическими томами и их размером, но сам по себе данные не дублирует. В стенде они реализованы "
    "параллельно: /dev/md0 демонстрирует зеркалирование, а vg_data/lv_logs хранит журнал приложения. "
    "В промышленной схеме LVM можно разместить поверх RAID и совместить обе функции."
)]
story += [p("2.3 Постоянство данных и сетевой контур", "H2RU")]
story += [p(
    "Каталог /mnt/logs подключён в контейнер как /var/www. Поэтому monitor.log сохраняется независимо "
    "от пересоздания контейнера и одновременно доступен встроенному HTTP-серверу. Контейнер привязан "
    "к 127.0.0.1:8080: внешний клиент не обходит Nginx, а TLS, редирект и access.log сосредоточены "
    "в одном пограничном компоненте."
)]
story += [p("2.4 Почему self-signed сертификат", "H2RU")]
story += [p(
    "Самоподписанный RSA-сертификат выбран из-за закрытого IP-адреса и отсутствия публичного доменного "
    "имени. Let’s Encrypt потребовал бы общедоступный домен и подтверждение владения; внутренняя PKI "
    "избыточна для одного учебного хоста. В production следует использовать сертификат доверенного "
    "центра с корректным SAN и автоматическим продлением; self-signed и curl -k там неприемлемы."
)]
story += [PageBreak()]

# Alternatives, fixes and conclusion
story += [p("3. Альтернативы, исправления и вывод", "H1RU")]
story += [p("3.1 Рассмотренные альтернативы", "H2RU")]
alternatives = [
    ["Решение", "Выбранный подход", "Почему не альтернатива"],
    ["Публикация порта", "Только 127.0.0.1 + Nginx", "0.0.0.0:8080 обошёл бы TLS и единое журналирование."],
    ["TLS", "Self-signed для лаборатории", "Let’s Encrypt невозможен без публичного домена; внутренняя PKI избыточна."],
    ["Запуск", "systemd управляет контейнером", "Ручной docker run не даёт системного автозапуска и единого статуса."],
    ["Хранилище", "LVM bind-mount", "Данные внутри writable layer исчезают при пересоздании контейнера."],
]
alt_table = Table([[p(x, "SmallRU") for x in row] for row in alternatives], colWidths=[33 * mm, 56 * mm, 85 * mm], repeatRows=1)
alt_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.35, LINE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [alt_table]
story += [p("3.2 Что не получилось с первого раза", "H2RU")]
fixes = [
    "В RED OS уже был установлен Docker CE: bootstrap.sh изменён так, чтобы установка выполнялась только при отсутствии команды docker.",
    "Каталоги для ключа и сертификата могли отсутствовать: перед openssl добавлено их явное создание.",
    "Стандартный server-блок RED OS перехватывал HTTP-запросы: deploy.sh сохраняет резервную копию и отключает только конфликтующий демонстрационный блок.",
]
for item in fixes:
    story += [p(f"• {item}")]
story += [p(
    "Эти исправления отражены отдельными коммитами, поэтому Git-история показывает реальный процесс "
    "диагностики и доработки, а не единовременную загрузку готового результата."
)]
story += [p("3.3 Итоговая самопроверка", "H2RU")]
check_rows = [
    ["Пункт", "Статус", "Доказательство"],
    ["1. Git", "Выполнено", "git log, README, public URL"],
    ["2. Скрипт", "Выполнено", "контрольный запуск"],
    ["3. Docker", "Выполнено", "build + healthy container"],
    ["4. RAID/LVM", "Выполнено", "[UU], lvs, df -h"],
    ["5. Nginx", "Выполнено", "nginx -t, HTTP 301"],
    ["6. TLS", "Выполнено", "HTTPS 200"],
    ["7. systemd", "Выполнено", "enabled, active"],
    ["8. Логи", "Выполнено", "journalctl + access.log"],
]
check = Table([[p(x, "SmallRU") for x in row] for row in check_rows], colWidths=[40 * mm, 35 * mm, 99 * mm], repeatRows=1)
check.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.35, LINE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
    ("TEXTCOLOR", (1, 1), (1, -1), GREEN),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story += [check, Spacer(1, 5 * mm)]
story += [callout("Вывод", "Все восемь пунктов технического чек-листа подтверждены свежим выводом команд. Репозиторий позволяет повторно развернуть стенд командой sudo ./bootstrap.sh и проверить маршрут запроса end-to-end.")]

doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
print(OUTPUT)
