#!/usr/bin/env python3
# native imports
import os
import re
import logging
import requests
import threading
import atexit
from urllib.request import urlopen
import json

# flask imports
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# installed imports
import colorlog

from backend import stream

GET_IP_URL = "http://myip.dnsomatic.com"  # prod
# GET_IP_URL = "http://127.0.0.1:5002"  # dev
AWS_URL = "http://flask-env.eba-iwmbbt73.us-east-2.elasticbeanstalk.com/ip"
# AWS_URL = "http://127.0.0.1:5001/"  # dev
GLOBALS = {}
INTERVAL = 20

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
    app.config[
        "PROPAGATE_EXCEPTIONS"
    ] = True  # SignatureExpired handling in prod, see https://github.com/vimalloc/flask-jwt-extended/issues/20

    # only if we're in prod, then use HTTPS only cookies
    app.config["JWT_COOKIE_SECURE"] = os.environ.get("USE_SECURE_COOKIES", False)

    return app


def shutdown():
    """
    TODO shut the camera streaming thread(s) down here.
    """
    LOGGER.info("Shutting down...")
    GLOBALS["thread_event"].set()
    for t in GLOBALS["threads"]:
        LOGGER.info(f"Waiting on {t} to join...")
        t.join()
        LOGGER.info(f"{t} joined")
    stream.stop_camera_thread()


def update_ip_thread():
    """
    Update the public website with the IP for this device.
    """
    last_good_ip = "1.2.3.4"
    while True:
        if GLOBALS["thread_event"].wait(INTERVAL):
            LOGGER.info("Signalled. Tearing down.")
            return

        # arbitrary placeholder
        try:
            LOGGER.debug(f"Making post request to... {GET_IP_URL}")
            response = requests.get(GET_IP_URL, timeout=3)
            ip = response.text
            if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip):
                LOGGER.debug(f"Ip is {ip}")
                if ip == last_good_ip:
                    LOGGER.debug("Skipping update, IP is the same as it used to be")
                    continue
                last_good_ip = ip
            else:
                LOGGER.debug(f"No IP in response, using {last_good_ip}")
                ip = last_good_ip
        except Exception as e:
            LOGGER.error(f"Error posting to public website: {e}")
        try:
            LOGGER.debug(f"Sending IP to {AWS_URL}")
            requests.post(AWS_URL, json={"ip": ip}, timeout=3)
        except Exception as e:
            LOGGER.error(f"Error posting to public website: {e}")
        finally:
            pass

    LOGGER.info("IP update thread exiting...")


def start_threads():
    """
    Start all threads and create signals
    """
    # start all background threads
    GLOBALS["threads"] = [threading.Thread(target=update_ip_thread)]

    # create a signal they'll terminate on
    GLOBALS["thread_event"] = threading.Event()

    for t in GLOBALS["threads"]:
        LOGGER.info(f"Starting {t}")
        t.start()


LOGGER.info("Registering shutdown function...")
atexit.register(shutdown)

# start the background threads
start_threads()

# initialize the app etc
flask_app = create_app()
db = create_db(flask_app)
api = create_api(flask_app)
jwt = create_jwt(flask_app)
