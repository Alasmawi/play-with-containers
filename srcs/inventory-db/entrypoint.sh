#!/bin/bash
set -euo pipefail

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
    gosu postgres initdb -D "$PGDATA" --auth=trust >/dev/null

    echo "listen_addresses='*'" >> "$PGDATA/postgresql.conf"
    echo "host all all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"

    gosu postgres pg_ctl -D "$PGDATA" -w start
    gosu postgres psql -v ON_ERROR_STOP=1 -c "CREATE ROLE \"${POSTGRES_USER}\" LOGIN PASSWORD '${POSTGRES_PASSWORD}';"
    gosu postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${POSTGRES_DB}\" OWNER \"${POSTGRES_USER}\";"
    gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop
fi

exec gosu postgres postgres -D "$PGDATA"
