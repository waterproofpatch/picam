#!/usr/bin/env python3
# native imports
import os
import logging

# flask imports
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# installed imports
import colorlog

basedir = os.path.abspath(os.path.dirname(__file__))

# get a logger for use everywhere
HANDLER = colorlog.StreamHandler()
HANDLER.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(filename)s:%(lineno)s:%(message)s"
    )
)

LOGGER = colorlog.getLogger(__name__)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)


def create_db(app):
    # database
    db = SQLAlchemy(app)
    return db


def create_api(app):
    # create the Api for endpoints (adding later)
    api = Api(app)
    return api


def create_jwt(app):
    # init the JWT manager
    jwt = JWTManager(app)
    return jwt


def allowed_file(filename):
    """
    Check if a filename has an extention that is allowed

    :param filename: the filename to check
    :return: True if the filename has an extension that is allowed
    :return: False otherwise
    """

    allowed_extensions = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def create_app():

    app = Flask(__name__, static_url_path="")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "app.db")
    )

    # figure out which db to use
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres"):
        LOGGER.debug("Using POSTGRES")
    else:
        LOGGER.debug("Using SQLite")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 megs
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "TEMPLATE_JWT_SECRET_KEY", "changemepls"
    )
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 15  # 15 minutes
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 60 * 60 * 24 * 30  # 30 days
    # TODO change this to True once we test this
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # only if we're in prod, then use HTTPS only cookies
    app.config["JWT_COOKIE_SECURE"] = os.environ.get("USE_SECURE_COOKIES", False)

    return app


def shutdown():
    """
    TODO shut the camera streaming thread(s) down here.
    """
    LOGGER.info("Shutting down...")


import atexit

LOGGER.info("Registering shutdown function...")
atexit.register(shutdown)

# initialize the app etc
flask_app = create_app()
db = create_db(flask_app)
api = create_api(flask_app)
jwt = create_jwt(flask_app)
