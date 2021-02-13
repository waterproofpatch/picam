# standard imports
import os
import datetime

# installed imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api


def create_app():
    """
    Create the Flask application object.
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///test.db"
    )
    return app


def create_db(app):
    """
    Create the SQLAlchemy db object
    """

    db = SQLAlchemy(app)
    db.init_app(app)
    return db


def create_api(app):
    """
    Create the SQLAlchemy db object
    """
    from .views import IpEndpoint

    api = Api(app)
    api.add_resource(IpEndpoint, "/ip")
    return api