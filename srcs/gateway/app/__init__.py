from flask import Flask

from .config import Config
from .inventory_routes import inventory_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(inventory_blueprint)
    return app
