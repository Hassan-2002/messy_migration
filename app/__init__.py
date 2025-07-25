from flask import Flask, jsonify
import logging
import os

from .db import close_db
from .error import APIError, handle_api_error
from .routes import register_routes

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'a_simple_default_secret_key'
    app.config['DATABASE_PATH'] = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'users.db'
    )
    app.config['JSON_SORT_KEYS'] = False
    app.config['LOG_LEVEL'] = logging.INFO
    app.config['LOG_FORMAT'] = '%(asctime)s - %(levelname)s - %(message)s'
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'

    logging.basicConfig(level=app.config['LOG_LEVEL'], format=app.config['LOG_FORMAT'])

    app.teardown_appcontext(close_db)

    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(Exception, handle_api_error)

    register_routes(app)

    @app.route('/')
    def Home():
        return jsonify({"status": "ok", "message": "User Management System"}), 200

    return app