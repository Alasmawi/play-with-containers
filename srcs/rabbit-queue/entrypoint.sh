#!/bin/bash
set -euo pipefail

RABBITMQ_USER="${RABBITMQ_USER:-guest}"
RABBITMQ_PASSWORD="${RABBITMQ_PASSWORD:-guest}"

rabbitmq-server -detached
for i in $(seq 1 30); do
    rabbitmqctl status >/dev/null 2>&1 && break
    sleep 1
done

if [ "$RABBITMQ_USER" != "guest" ]; then
    rabbitmqctl user_exists "$RABBITMQ_USER" || rabbitmqctl add_user "$RABBITMQ_USER" "$RABBITMQ_PASSWORD"
    rabbitmqctl set_user_tags "$RABBITMQ_USER" administrator
    rabbitmqctl set_permissions -p / "$RABBITMQ_USER" ".*" ".*" ".*"
else
    rabbitmqctl set_permissions -p / guest ".*" ".*" ".*"
fi

rabbitmqctl stop
exec rabbitmq-server
