FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-15 gosu && \
    pg_dropcluster --stop 15 main && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/postgresql/15/bin:${PATH}"
ENV PGDATA=/var/lib/postgresql/data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p "$PGDATA" && chown postgres:postgres "$PGDATA"

VOLUME ["/var/lib/postgresql/data"]
EXPOSE 5432
# SIGINT = "fast shutdown": disconnect clients and exit cleanly instead of waiting on them.
STOPSIGNAL SIGINT
ENTRYPOINT ["/entrypoint.sh"]
