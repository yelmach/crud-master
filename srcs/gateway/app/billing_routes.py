"""Gateway route for billing messages."""

from __future__ import annotations

import json

import pika
from pika.exceptions import AMQPConnectionError, AMQPError
from flask import Blueprint, current_app, jsonify, request


billing_blueprint = Blueprint("billing", __name__)


def _billing_connection_parameters() -> pika.ConnectionParameters:
	return pika.ConnectionParameters(
		host=current_app.config["BILLING_RABBITMQ_HOST"],
		port=current_app.config["BILLING_RABBITMQ_PORT"],
		credentials=pika.PlainCredentials(
			current_app.config["BILLING_RABBITMQ_USER"],
			current_app.config["BILLING_RABBITMQ_PASSWORD"],
		),
	)


@billing_blueprint.route("/api/billing", methods=["POST"], strict_slashes=False)
def publish_billing_message():
	"""Queue billing messages in RabbitMQ and return immediately."""

	payload = request.get_json(silent=True)
	if payload is None:
		return jsonify(error="Request body must be valid JSON"), 400

	try:
		connection = pika.BlockingConnection(_billing_connection_parameters())
		channel = connection.channel()
		channel.queue_declare(queue=current_app.config["BILLING_RABBITMQ_QUEUE"], durable=True)
		channel.basic_publish(
			exchange="",
			routing_key=current_app.config["BILLING_RABBITMQ_QUEUE"],
			body=json.dumps(payload),
			properties=pika.BasicProperties(delivery_mode=2),
		)
		connection.close()
		return jsonify(message="Message posted"), 200
	except (AMQPConnectionError, AMQPError) as exc:
		current_app.logger.error(f"Failed to publish billing message: {exc}")
		return jsonify(error="Billing queue is currently unavailable"), 503
