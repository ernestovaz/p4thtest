FROM alpine:latest

RUN apk add net-tools iproute2 scapy ethtool iperf libcap-dev
COPY send.py different_send.py forward.py receive.py /scripts/
