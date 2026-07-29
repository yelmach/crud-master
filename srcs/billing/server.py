"""Entrypoint for the billing Flask service."""

from app import create_app


app = create_app()


if __name__ == "__main__":
	app.run(
		host=app.config["BILLING_HOST"],
		port=app.config["BILLING_PORT"],
		debug=app.config["DEBUG"],
	)

