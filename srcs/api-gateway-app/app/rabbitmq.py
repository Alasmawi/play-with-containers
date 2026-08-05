import json
import os
import ssl

import pika


def connection_parameters(**overrides):
    """Broker connection settings, shared by the publisher and the consumer.

    RABBITMQ_HOST accepts either a bare hostname or a full AMQP URI
    (`amqps://host:5671`), because managed brokers -- Amazon MQ among them --
    advertise their endpoint as a URI while pika wants the host on its own.
    """
    host = os.environ["RABBITMQ_HOST"]
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.split("/", 1)[0].split(":", 1)[0]

    port = int(os.environ.get("RABBITMQ_PORT", 5672))
    user = os.environ.get("RABBITMQ_USER", "guest")
    password = os.environ.get("RABBITMQ_PASSWORD", "guest")

    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.PlainCredentials(user, password),
        **overrides,
    )

    # Self-hosted brokers here speak plain AMQP; managed ones (Amazon MQ)
    # accept nothing but AMQPS, so TLS is opt-in per deployment.
    if os.environ.get("RABBITMQ_USE_TLS", "").lower() in ("1", "true", "yes"):
        parameters.ssl_options = pika.SSLOptions(ssl.create_default_context(), host)

    return parameters


def publish_billing_message(payload: dict):
    queue_name = os.environ.get("BILLING_QUEUE", "billing_queue")

    connection = pika.BlockingConnection(connection_parameters())
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
    finally:
        connection.close()
