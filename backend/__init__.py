"""
Init file.
"""
#!/usr/bin/env python3

# standard imports
import os
import re
import threading
from urllib.request import urlopen
import atexit
import json
import time

# installed imports
import requests
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# project imports
from backend.logger import LOGGER

GET_IP_URL = "http://myip.dnsomatic.com"  # prod
# GET_IP_URL = "http://127.0.0.1:5002"  # dev
AWS_URL = "http://flask-env.eba-iwmbbt73.us-east-2.elasticbeanstalk.com/ip"
# AWS_URL = "http://127.0.0.1:5001/"  # dev
GLOBALS = {}
INTERVAL = 5
IP_UPDATE_DELAY = 20

basedir = os.path.abspath(os.path.dirname(__file__))


def create_db(app):
    """
    database
    """
    return SQLAlchemy(app)


def create_api(app):
    """
    create the Api for endpoints (adding later)
    """
    return Api(app)


def create_jwt(app):
    """
    init the JWT manager
    """
    return JWTManager(app)


def create_app():
    """
    Creates the flask application.
    """

    LOGGER.debug("Backend web service registering shutdown function...")
    atexit.register(shutdown)

    # start the background threads
    start_threads()

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
    app.config["PROPAGATE_EXCEPTIONS"] = True
    # SignatureExpired handling in prod, see
    # https://github.com/vimalloc/flask-jwt-extended/issues/20

    # only if we're in prod, then use HTTPS only cookies
    app.config["JWT_COOKIE_SECURE"] = os.environ.get("USE_SECURE_COOKIES", False)

    return app


def shutdown():
    """
    Shutdown the IP update thread here.
    """
    LOGGER.debug("Shutting down IP thread...")
    GLOBALS["thread_event"].set()
    for thread in GLOBALS["threads"]:
        LOGGER.debug("Waiting on %s to join...", thread)
        thread.join()
        LOGGER.debug("%s joined", thread)


def start_threads():
    """
    Start all threads and create events.
    """
    # start all background threads
    GLOBALS["threads"] = [threading.Thread(target=update_ip_thread)]

    # create a signal they'll terminate on
    GLOBALS["thread_event"] = threading.Event()

    for thread in GLOBALS["threads"]:
        LOGGER.debug("Starting %s", thread)
        thread.start()


def update_ip_thread():
    """
    Update the public website with the IP for this device.
    """
    last_good_ip = "1.2.3.4"
    last_send = time.time()
    while True:
        if GLOBALS["thread_event"].wait(INTERVAL):
            LOGGER.debug("Signalled. Tearing down.")
            return

        # throttle the IP updates
        if time.time() - last_send < IP_UPDATE_DELAY:
            LOGGER.debug(
                "Waiting %d more seconds before updating IP...",
                IP_UPDATE_DELAY - (time.time() - last_send),
            )
            continue

        # arbitrary placeholder
        try:
            last_send = time.time()
            LOGGER.debug("Making post request to %s", GET_IP_URL)
            response = requests.get(GET_IP_URL, timeout=3)
            my_public_ip = response.text
            if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", my_public_ip):
                LOGGER.debug("Ip is %s", my_public_ip)
                if my_public_ip == last_good_ip:
                    LOGGER.debug("Skipping update, IP is the same as it used to be")
                    continue
            else:
                LOGGER.debug("No IP in response, will try later...")
                continue
        except ConnectionError as connection_error:
            LOGGER.error("Error getting public IP: %s", connection_error)
        try:
            LOGGER.debug("Sending IP to %s", AWS_URL)
            requests.post(AWS_URL, json={"ip": my_public_ip}, timeout=3)
            last_good_ip = my_public_ip
        except ConnectionError as connection_error:
            LOGGER.error("Error posting to public website: %s", connection_error)
        finally:
            pass

    LOGGER.debug("IP update thread exiting...")


# initialize the app etc
flask_app = create_app()
db = create_db(flask_app)
api = create_api(flask_app)
jwt = create_jwt(flask_app)
