#!/usr/bin/env python3
"""
This is the main entry point for the app.

UWSGI: module: app(.py), callable: app
"""

# native imports
import sys
import base64
import argparse

# flask imports
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# my imports, some from __init__
from backend import flask_app, api, views, db, models
from . import LOGGER

api.add_resource(views.Images, "/api/images")
api.add_resource(views.Register, "/api/register")
api.add_resource(views.Login, "/api/login")
api.add_resource(views.Logout, "/api/logout")
api.add_resource(views.TokenRefresh, "/api/refresh")


def init_db(db, drop_all=False):
    """
    Initialize the database
    """
    LOGGER.info("Initializing DB {}".format(db))
    db.init_app(flask_app)
    if drop_all:
        LOGGER.info("Dropping tables...")
        db.drop_all()
    db.create_all()

    image = models.Image(url="test.png")
    db.session.add(image)

    db.session.commit()


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
        sys.exit(0)

    LOGGER.info("Running app from flask!")
    flask_app.run(debug=True)
