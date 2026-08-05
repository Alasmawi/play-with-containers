# play-with-containers

The `crud-master` movie-streaming microservices, fully containerized: six purpose-built images
(no pre-built Docker Hub images except the `debian:bullseye-slim` base), one Docker network, and
three named volumes, all managed exclusively through `docker-compose`.

## Architecture

```
                         host:3000
                             │
                    ┌────────▼─────────┐
                    │  api-gateway-app │  (published to host)
                    └──┬─────────────┬─┘
                HTTP   │             │  publish (AMQP)
                       ▼             ▼
              ┌────────────────┐  ┌──────────────┐        ┌──────────────┐
              │  inventory-app │  │ rabbit-queue │◄───────┤ billing-app  │
              │   (:8080)      │  └──────────────┘        │  (:8080)     │
              └───────┬────────┘                          └──────┬───────┘
                      ▼                                          ▼
              ┌────────────────┐                          ┌──────────────┐
              │  inventory-db  │                          │  billing-db  │
              │   (:5432)      │                          │   (:5432)    │
              └────────────────┘                          └──────────────┘

     all six containers share the "crud-net" bridge network;
     only api-gateway-app is published to the host (port 3000)
```

## Containers (all built from source, `debian:bullseye-slim`)

| Container         | Built from apt package(s)                | Notes |
|--------------------|------------------------------------------|-------|
| `inventory-db`     | `postgresql-13`                          | hosts `movies_db`, volume `inventory-db` |
| `billing-db`       | `postgresql-13`                          | hosts `billing_db`, volume `billing-db` |
| `rabbit-queue`     | `rabbitmq-server`                        | hosts `billing_queue` |
| `inventory-app`    | `python3` + our Flask app                | CRUD API, connects to `inventory-db` |
| `billing-app`      | `python3` + our pika consumer            | consumes `billing_queue`, writes to `billing-db`; a tiny stdlib HTTP server on :8080 exists only so the container satisfies "accessible via port 8080" — the actual billing logic has no HTTP surface |
| `api-gateway-app`  | `python3` + our Flask app                | only container published to the host, on port 3000; logs to volume `api-gateway-app` |

None of the database/queue containers use the official `postgres`/`rabbitmq` Docker Hub images —
each `Dockerfile` starts from bare Debian and installs the server via `apt-get`, with a custom
`entrypoint.sh` that initializes the data directory / vhost on first boot only (subsequent boots
reuse the named volume).

## Configuration

All credentials live in `.env` (gitignored, per spec) and are injected into containers via
`docker-compose.yml` — nothing is hardcoded in source or in the compose file itself.
[`.env.example`](.env.example) lists every key the compose file expects — `INVENTORY_DB_*`,
`BILLING_DB_*`, `RABBITMQ_USER`/`RABBITMQ_PASSWORD`, `BILLING_QUEUE` — with throwaway values.

`RABBITMQ_USER` must not be `guest`: RabbitMQ refuses that account on any connection that isn't
loopback, and every client here reaches the broker across the `crud-net` bridge. `rabbit-queue`'s
entrypoint refuses to start with it and deletes the account outright.

## Running

```bash
cp .env.example .env   # then fill in real passwords
docker-compose build
docker-compose up -d
docker-compose ps
```

Try it:

```bash
curl -X POST http://localhost:3000/api/movies \
  -H "Content-Type: application/json" \
  -d '{"title":"Dune","description":"Spice must flow"}'

curl -X POST http://localhost:3000/api/billing \
  -H "Content-Type: application/json" \
  -d '{"user_id":"5","number_of_items":"2","total_amount":"40"}'
```

Tear down (and drop volumes, for a truly clean slate):

```bash
docker-compose down -v
```

## What's verified, and what isn't

- All six images build cleanly from `debian:bullseye-slim` with no other pre-built images.
- Full request flow through the gateway: movie CRUD proxied to `inventory-app`, billing messages
  published to `rabbit-queue` and consumed into `billing-db.orders`.
- `restart: unless-stopped`: killing a container's main process (`docker exec inventory-app kill 1`)
  results in Docker restarting it automatically.
- `api-gateway-app`'s log volume persists Flask/werkzeug access logs across container restarts.
- Only `api-gateway-app` publishes a host port (3000); every other container is reachable solely
  over the internal `crud-net` network, matching "any outside request must be able to access only
  the api-gateway-app."

Not verified: a rebuild against the current `rabbit-queue` entrypoint, which now refuses to start on
`RABBITMQ_USER=guest` and provisions the user through `list_users` rather than the `user_exists`
subcommand it was calling before — `rabbitmqctl` has no such subcommand, so that branch was falling
through to `add_user` on every restart.

## Design notes

- Each app container builds its own Python venv inside the image (not bind-mounted), so the image
  is self-contained and reproducible.
- `inventory-db`/`billing-db` use a from-scratch `initdb` (not Debian's auto-created cluster) so the
  named volume mount behaves predictably: empty volume → initialize once; populated volume → reuse
  as-is, no re-init.
- `billing-app`'s health endpoint is a plain `http.server` on a daemon thread — deliberately not
  Flask, to keep the service's dependency footprint identical to `crud-master`'s (pika + SQLAlchemy
  only) and to make clear it's a liveness probe, not part of the billing API surface.
