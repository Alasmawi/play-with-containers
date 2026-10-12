FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends rabbitmq-server && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5672
ENTRYPOINT ["/entrypoint.sh"]
