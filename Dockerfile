FROM python:3.10.6-alpine3.16

ENV NAMESERVER 1.0.0.1
ENV NAMESERVER_PORT 853

WORKDIR /root
COPY dns-over-tls-proxy.py .

EXPOSE 30853/tcp
EXPOSE 30853/udp

CMD ["python","dns-over-tls-proxy.py"]