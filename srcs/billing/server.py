"""Entrypoint for the billing Flask service."""

from app import create_app
from app.billing_consumer import start_consumer_thread


app = create_app()


if __name__ == "__main__":
	start_consumer_thread(app)
	app.run(
		host=app.config["BILLING_HOST"],
		port=app.config["BILLING_PORT"],
		debug=app.config["DEBUG"],
	)

