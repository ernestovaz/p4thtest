FROM alpine:latest

RUN apk add net-tools iproute2 scapy ethtool iperf libcap-dev
