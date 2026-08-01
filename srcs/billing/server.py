from app import create_app
from app.billing_consumer import start_consuming

app = create_app()

if __name__ == "__main__":
    start_consuming(app)