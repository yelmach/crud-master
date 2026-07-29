"""Billing service configuration.

The service reads all infrastructure settings from environment variables so the
deployment can be configured by Vagrant or the VM shell without hard-coded
credentials.
"""

from __future__ import annotations

import os


def _env(name: str, default: str | None = None) -> str:
	value = os.getenv(name, default)
	if value is None:
		raise RuntimeError(f"Missing required environment variable: {name}")
	return value


def _bool_env(name: str, default: str = "false") -> bool:
	return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def build_postgres_uri() -> str:
	user = _env("BILLING_DB_USER", "billing_user")
	password = _env("BILLING_DB_PASSWORD", "billing_password")
	host = _env("BILLING_DB_HOST", "localhost")
	port = _env("BILLING_DB_PORT", "5432")
	database = _env("BILLING_DB_NAME", "billing_db")
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
			"BILLING_RABBITMQ_HOST": _env("BILLING_RABBITMQ_HOST", "localhost"),
			"BILLING_RABBITMQ_PORT": int(_env("BILLING_RABBITMQ_PORT", "5672")),
			"BILLING_RABBITMQ_USER": _env("BILLING_RABBITMQ_USER", "guest"),
			"BILLING_RABBITMQ_PASSWORD": _env("BILLING_RABBITMQ_PASSWORD", "guest"),
			"BILLING_RABBITMQ_QUEUE": _env("BILLING_RABBITMQ_QUEUE", "billing_queue"),
			"BILLING_HOST": _env("BILLING_HOST", "0.0.0.0"),
			"BILLING_PORT": int(_env("BILLING_PORT", "5001")),
		}

