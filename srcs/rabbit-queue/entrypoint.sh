#!/bin/bash
set -euo pipefail

: "${RABBITMQ_USER:?RABBITMQ_USER is required (see .env.example)}"
: "${RABBITMQ_PASSWORD:?RABBITMQ_PASSWORD is required (see .env.example)}"

# The built-in `guest` account is refused on every connection that isn't
# loopback, and each client here reaches this container across the
# crud-net bridge -- so a real user is required, and `guest` is deleted
# rather than left listening with a default password.
if [ "$RABBITMQ_USER" = "guest" ]; then
    echo "RABBITMQ_USER must not be 'guest': RabbitMQ rejects it from anywhere but localhost." >&2
    exit 1
fi

rabbitmq-server -detached
for i in $(seq 1 30); do
    rabbitmqctl status >/dev/null 2>&1 && break
    sleep 1
done

if rabbitmqctl list_users --formatter json | grep -q "\"$RABBITMQ_USER\""; then
    rabbitmqctl change_password "$RABBITMQ_USER" "$RABBITMQ_PASSWORD"
else
    rabbitmqctl add_user "$RABBITMQ_USER" "$RABBITMQ_PASSWORD"
fi
rabbitmqctl set_user_tags "$RABBITMQ_USER" administrator
rabbitmqctl set_permissions -p / "$RABBITMQ_USER" ".*" ".*" ".*"
rabbitmqctl delete_user guest 2>/dev/null || true

rabbitmqctl stop
exec rabbitmq-server
