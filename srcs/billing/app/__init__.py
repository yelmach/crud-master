"""Billing application factory."""

from flask import Flask

from .config import BillingConfig
from .database import db, init_database


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_mapping(BillingConfig.as_dict())
	db.init_app(app)

	with app.app_context():
		init_database()

	@app.get("/")
	def home() -> tuple[dict[str, str], int]:
		return {"message": "Billing service is running"}, 200

	@app.get("/health")
	def health() -> tuple[dict[str, str], int]:
		return {"status": "ok"}, 200

	@app.get("/api/health")
	def api_health() -> tuple[dict[str, str], int]:
		return {"status": "ok"}, 200

	return app

