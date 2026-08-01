from flask import Flask, jsonify
from .config import Config
from .billing_routes import billing_blueprint
from .inventory_routes import inventory_blueprint


def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    app.register_blueprint(inventory_blueprint)
    app.register_blueprint(billing_blueprint)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify(error=error.description or "Bad request"), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(error="Not found"), 404
    
    return app
