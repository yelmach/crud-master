from flask import Flask

from .config import Config
from .billing_routes import billing_blueprint
from .inventory_routes import inventory_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(inventory_blueprint)
    app.register_blueprint(billing_blueprint)
    return app
