FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www
COPY script.sh /usr/local/bin/script.sh
RUN chmod +x /usr/local/bin/script.sh

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=2)" || exit 1

CMD ["/bin/bash", "-c", "MONITOR_LOG=/var/www/monitor.log /usr/local/bin/script.sh & exec python3 -m http.server 8080 --directory /var/www"]
