import json
import logging
import os
import ssl
import time

import pika

from app.db import Order, get_session_factory

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("billing-consumer")


def connect():
    # RABBITMQ_HOST accepts either a bare hostname or a full AMQP URI
    # (`amqps://host:5671`), because managed brokers -- Amazon MQ among
    # them -- advertise their endpoint as a URI while pika wants the host
    # on its own.
    host = os.environ["RABBITMQ_HOST"]
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.split("/", 1)[0].split(":", 1)[0]

    port = int(os.environ.get("RABBITMQ_PORT", 5672))
    user = os.environ.get("RABBITMQ_USER", "guest")
    password = os.environ.get("RABBITMQ_PASSWORD", "guest")

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(host=host, port=port, credentials=credentials, heartbeat=30)

    # Self-hosted brokers here speak plain AMQP; managed ones (Amazon MQ)
    # accept nothing but AMQPS, so TLS is opt-in per deployment.
    if os.environ.get("RABBITMQ_USE_TLS", "").lower() in ("1", "true", "yes"):
        parameters.ssl_options = pika.SSLOptions(ssl.create_default_context(), host)

    while True:
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ not reachable yet, retrying in 3s...")
            time.sleep(3)


def run():
    queue_name = os.environ.get("BILLING_QUEUE", "billing_queue")
    session_factory = get_session_factory()

    connection = connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)

    def on_message(ch, method, _properties, body):
        session = session_factory()
        try:
            try:
                payload = json.loads(body)
                order = Order(
                    user_id=str(payload["user_id"]),
                    number_of_items=int(payload["number_of_items"]),
                    total_amount=float(payload["total_amount"]),
                )
            except (ValueError, TypeError, KeyError):
                # The message itself is wrong, so no amount of retrying
                # fixes it -- requeueing would just redeliver it forever
                # and block the queue behind it. Drop it, loudly.
                logger.exception("Discarding malformed message: %r", body)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return

            session.add(order)
            session.commit()
            logger.info("Stored order for user_id=%s", order.user_id)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            # The message was fine and the write failed (database down,
            # connection dropped) -- that is worth retrying, so requeue.
            session.rollback()
            logger.exception("Failed to store order, requeueing")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        finally:
            session.close()

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    logger.info("Billing consumer started, waiting for messages on '%s'", queue_name)
    channel.start_consuming()
