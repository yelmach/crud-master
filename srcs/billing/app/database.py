"""Database extension for the billing service."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError, SQLAlchemyError


db = SQLAlchemy()


class Order(db.Model):
	"""Orders saved by the billing consumer after RabbitMQ message processing."""

	__tablename__ = "orders"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, nullable=False)
	number_of_items = db.Column(db.Integer, nullable=False)
	total_amount = db.Column(db.Numeric(10, 2), nullable=False)

	def to_dict(self) -> dict[str, object]:
		return {
			"id": self.id,
			"user_id": self.user_id,
			"number_of_items": self.number_of_items,
			"total_amount": str(self.total_amount),
		}


def init_database() -> None:
	"""Create/validate tables and fail with an explicit message if DB is unreachable."""

	try:
		db.create_all()
	except OperationalError as exc:
		raise RuntimeError(
			"Unable to connect to PostgreSQL for billing_db. "
			"Check BILLING_DB_HOST, BILLING_DB_PORT, BILLING_DB_USER, BILLING_DB_PASSWORD, and BILLING_DB_NAME."
		) from exc
	except SQLAlchemyError as exc:
		raise RuntimeError(f"Database initialization failed: {exc}") from exc


def insert_order(user_id: str | int, number_of_items: str | int, total_amount: str | int | float) -> Order:
	"""Persist one order and return the saved row."""

	try:
		clean_user_id = int(user_id)
		clean_number_of_items = int(number_of_items)
		clean_total_amount = Decimal(str(total_amount))
	except (TypeError, ValueError, InvalidOperation) as exc:
		raise ValueError("Invalid billing payload values. Expected numeric user_id, number_of_items, and total_amount.") from exc

	order = Order(
		user_id=clean_user_id,
		number_of_items=clean_number_of_items,
		total_amount=clean_total_amount,
	)

	try:
		db.session.add(order)
		db.session.commit()
		return order
	except SQLAlchemyError as exc:
		db.session.rollback()
		raise RuntimeError(f"Failed to insert billing order into database: {exc}") from exc

