FROM alpine:latest
LABEL maintainer "Kodiak Firesmith <kodiak@firesmith.org>"

RUN apk add python3
RUN mkdir /etc/ddns-updater

COPY ddns-updater.py /usr/bin/

ENTRYPOINT ["/usr/bin/ddns-updater.py"]