"""RabbitMQ consumer for billing messages."""

from __future__ import annotations

import json
import threading
import time
from typing import Any

import pika
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker

from .database import insert_order


REQUIRED_FIELDS = ("user_id", "number_of_items", "total_amount")


def parse_message_body(body: bytes) -> dict[str, Any]:
	"""Decode and parse one RabbitMQ message body as JSON object."""

	try:
		decoded = body.decode("utf-8")
	except UnicodeDecodeError as exc:
		raise ValueError("Message body is not valid UTF-8.") from exc

	try:
		payload = json.loads(decoded)
	except json.JSONDecodeError as exc:
		raise ValueError("Message body is not valid JSON.") from exc

	if not isinstance(payload, dict):
		raise ValueError("Message JSON must be an object.")

	return payload


def validate_payload(payload: dict[str, Any]) -> None:
	"""Validate that all required billing fields are present and non-empty."""

	missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
	if missing_fields:
		raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

	empty_fields = [
		field
		for field in REQUIRED_FIELDS
		if payload[field] is None or (isinstance(payload[field], str) and payload[field].strip() == "")
	]
	if empty_fields:
		raise ValueError(f"Required fields cannot be empty: {', '.join(empty_fields)}")


def process_billing_message(channel: Any, delivery_tag: int, body: bytes, app: Any) -> None:
	"""Parse, validate, and persist a billing message; ack only if insert succeeds."""

	with app.app_context():
		try:
			payload = parse_message_body(body)
			validate_payload(payload)
			insert_order(
				user_id=payload["user_id"],
				number_of_items=payload["number_of_items"],
				total_amount=payload["total_amount"],
			)
			channel.basic_ack(delivery_tag=delivery_tag)
			print("[billing-consumer] Message processed and acknowledged")
		except Exception as exc:  # Keep message unacked on failure by using nack with requeue.
			print(f"[billing-consumer] Failed to process message: {exc}")
			channel.basic_nack(delivery_tag=delivery_tag, requeue=True)


def _connection_parameters(app: Any) -> pika.ConnectionParameters:
	credentials = pika.PlainCredentials(
		app.config["BILLING_RABBITMQ_USER"],
		app.config["BILLING_RABBITMQ_PASSWORD"],
	)
	return pika.ConnectionParameters(
		host=app.config["BILLING_RABBITMQ_HOST"],
		port=app.config["BILLING_RABBITMQ_PORT"],
		credentials=credentials,
	)


def consume_billing_queue(app: Any) -> None:
	"""Consume billing messages forever, reconnecting if RabbitMQ is temporarily unavailable."""

	queue_name = app.config["BILLING_RABBITMQ_QUEUE"]

	while True:
		try:
			connection = pika.BlockingConnection(_connection_parameters(app))
			channel = connection.channel()
			channel.queue_declare(queue=queue_name, durable=True)
			channel.basic_qos(prefetch_count=1)

			def _callback(ch: Any, method: Any, _properties: Any, body: bytes) -> None:
				process_billing_message(ch, method.delivery_tag, body, app)

			channel.basic_consume(queue=queue_name, on_message_callback=_callback, auto_ack=False)
			print(f"[billing-consumer] Waiting for messages on queue '{queue_name}'")
			channel.start_consuming()
		except (AMQPConnectionError, ChannelClosedByBroker) as exc:
			print(f"[billing-consumer] RabbitMQ unavailable: {exc}. Retrying in 5 seconds...")
			time.sleep(5)
		except KeyboardInterrupt:
			print("[billing-consumer] Stopped by user")
			break


def start_consumer_thread(app: Any) -> threading.Thread:
	"""Start RabbitMQ consumer in a daemon thread so Flask server can keep running."""

	thread = threading.Thread(target=consume_billing_queue, args=(app,), daemon=True, name="billing-consumer")
	thread.start()
	return thread

