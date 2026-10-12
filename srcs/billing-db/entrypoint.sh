#!/bin/bash
set -euo pipefail

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

# First boot only: an empty volume gets a fresh cluster; a populated one is reused as-is.
if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
    gosu postgres initdb -D "$PGDATA" --auth=trust >/dev/null

    echo "listen_addresses='*'" >> "$PGDATA/postgresql.conf"
    echo "host all all 0.0.0.0/0 scram-sha-256" >> "$PGDATA/pg_hba.conf"

    # Temporary server on the unix socket only, so nothing can connect before setup is done.
    gosu postgres pg_ctl -D "$PGDATA" -o "-c listen_addresses=''" -w start
    # psql variables (:"ident", :'literal') quote safely, whatever the password contains.
    gosu postgres psql -v ON_ERROR_STOP=1 \
        -v dbuser="$POSTGRES_USER" -v dbpass="$POSTGRES_PASSWORD" -v dbname="$POSTGRES_DB" <<'SQL'
CREATE ROLE :"dbuser" LOGIN PASSWORD :'dbpass';
CREATE DATABASE :"dbname" OWNER :"dbuser";
SQL
    gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop
fi

exec gosu postgres postgres -D "$PGDATA"
