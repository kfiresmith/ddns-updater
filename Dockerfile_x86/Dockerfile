FROM alpine:latest
LABEL maintainer "Kodiak Firesmith <kodiak@firesmith.org>"

RUN apk add python3

COPY ddns-updater.py /usr/bin/
COPY ddns-updater.conf /etc/ddns-updater/

ENTRYPOINT ["/usr/bin/ddns-updater.py"]