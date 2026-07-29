"""Billing service configuration.

The service loads settings from the project .env file, with process environment
variables still able to override values when needed.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH = PROJECT_ROOT / ".env"

# Load shared variables from the repository root.
load_dotenv(dotenv_path=DOTENV_PATH, override=False)


def _bool_env(name: str, default: str = "false") -> bool:
	return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def build_postgres_uri() -> str:
	user = os.getenv("BILLING_DB_USER", "billing_user")
	password = os.getenv("BILLING_DB_PASSWORD", "billing_password")
	host = os.getenv("BILLING_DB_HOST", "localhost")
	port = os.getenv("BILLING_DB_PORT", "5432")
	database = os.getenv("BILLING_DB_NAME", "billing_db")
	return f"postgresql://{user}:{password}@{host}:{port}/{database}"


class BillingConfig:
	"""Settings used by the billing Flask application."""

	@staticmethod
	def as_dict() -> dict[str, object]:
		return {
			"DEBUG": _bool_env("BILLING_DEBUG", "false"),
			"TESTING": _bool_env("BILLING_TESTING", "false"),
			"JSON_SORT_KEYS": False,
			"SQLALCHEMY_DATABASE_URI": os.getenv("BILLING_DATABASE_URI", build_postgres_uri()),
			"SQLALCHEMY_TRACK_MODIFICATIONS": False,
			"BILLING_RABBITMQ_HOST": os.getenv("BILLING_RABBITMQ_HOST", "localhost"),
			"BILLING_RABBITMQ_PORT": int(os.getenv("BILLING_RABBITMQ_PORT", "5672")),
			"BILLING_RABBITMQ_USER": os.getenv("BILLING_RABBITMQ_USER", "guest"),
			"BILLING_RABBITMQ_PASSWORD": os.getenv("BILLING_RABBITMQ_PASSWORD", "guest"),
			"BILLING_RABBITMQ_QUEUE": os.getenv("BILLING_RABBITMQ_QUEUE", "billing_queue"),
			"BILLING_RABBITMQ_HEARTBEAT": int(os.getenv("BILLING_RABBITMQ_HEARTBEAT", "30")),
			"BILLING_RABBITMQ_BLOCKED_CONNECTION_TIMEOUT": int(
				os.getenv("BILLING_RABBITMQ_BLOCKED_CONNECTION_TIMEOUT", "30")
			),
			"BILLING_CONSUMER_RECONNECT_DELAY": int(os.getenv("BILLING_CONSUMER_RECONNECT_DELAY", "5")),
			"BILLING_HOST": os.getenv("BILLING_HOST", "0.0.0.0"),
			"BILLING_PORT": int(os.getenv("BILLING_PORT", "5001")),
		}

