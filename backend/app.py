#!/usr/bin/env python3
"""
This is the main entry point for the app.

UWSGI: module: app(.py), callable: app
"""

# native imports
import sys
import os
import base64
import argparse

# flask imports
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# my imports, some from __init__
from backend import flask_app, api, views, db, models, stream
from . import LOGGER, shutdown

api.add_resource(views.Images, "/api/images")
api.add_resource(views._Image, "/api/images/<int:id>")
api.add_resource(views.Login, "/api/login")
api.add_resource(views.Logout, "/api/logout")
api.add_resource(views.TokenRefresh, "/api/refresh")


def add_default_user():
    """
    Add a user to the database. On the production system,
    LOGIN_EMAIL and LOGIN_PASSWORD must be set in order for legitimate
    credentials to be applied. If these environment variables are not set,
    the hardcoded credentials will be applied.
    """
    # add the test user. If the environment variables are not set, the
    # credentials are assumed to be dummy credentials.
    if (
        models.User.query.filter_by(
            email=os.environ.get("LOGIN_EMAIL", "test@gmail.com")
        ).first()
        is None
    ):
        hashed_pw = models.User.generate_hash(
            plaintext_password=os.environ.get(
                "LOGIN_PASSWORD", "passwordpassword"
            ).encode()
        )
        new_user = models.User(
            email=os.environ.get("LOGIN_EMAIL", "test@gmail.com"),
            password=base64.b64encode(hashed_pw).decode(),
        )
        LOGGER.debug(f"Adding user {new_user}...")
        db.session.add(new_user)
        db.session.commit()


def init_db(db, drop_all=False):
    """
    Initialize the database.
    """
    LOGGER.info(f"Initializing DB {db}")
    db.init_app(flask_app)

    if drop_all:
        LOGGER.info("Dropping tables...")
        db.drop_all()

    db.create_all()
    db.session.commit()

    add_default_user()


if __name__ == "__main__":
    """
    Entry point
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dropall",
        action="store_true",
        required=False,
        help="drop tables in database before starting",
    )

    parser.add_argument(
        "--initonly",
        action="store_true",
        required=False,
        help="just init database and do nothing else",
    )

    args = parser.parse_args()

    init_db(db, drop_all=args.dropall)
    if args.initonly:
        stream.stop_camera_thread()
        shutdown()
        sys.exit(0)

    LOGGER.info("Running app in debug mode from Flask")
    try:
        flask_app.run(debug=True)
    except SystemExit:
        LOGGER.info("Flask app shutting down...")
        shutdown()
        stream.stop_camera_thread()
        sys.exit(
            3
        )  # allows werkzeug to continue on to reload, see werkzeug/_reloader.py line 184
