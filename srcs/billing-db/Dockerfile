FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-13 gosu && \
    pg_dropcluster --stop 13 main && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/postgresql/13/bin:${PATH}"
ENV PGDATA=/var/lib/postgresql/data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p "$PGDATA" && chown postgres:postgres "$PGDATA"

VOLUME ["/var/lib/postgresql/data"]
EXPOSE 5432
ENTRYPOINT ["/entrypoint.sh"]
