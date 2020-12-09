"""
Views backend. Handles items, logins, registrations, logouts and tokens.
"""
# native imports
import base64
import bcrypt
import os
import uuid
import time

# flask imports
from flask import jsonify, send_from_directory
from flask_restful import Resource, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from werkzeug.utils import secure_filename

from backend.models import User, Image, RevokedTokenModel

# my imports, from __init__
from backend import jwt, db, flask_app, allowed_file, LOGGER

# globals
PASSWORD_MIN_LEN = 13


@flask_app.route("/cam/<path:path>")
def send_images(path):
    """
    Image file resolution for development
    """
    return send_from_directory("cam", path)


class Images(Resource):
    """
    Images endpoint

    Arguments:
        Resource {Resource} - Flask resource

    Returns:
        tuple - {'message'}, status_code
    """

    def get(self):
        """
        Handle a get request for all files
        """
        return [x.as_json() for x in Image.query.all()]

    def post(self):
        """
        Start the camera and take a picture.
        """
        print("starting capture...")
        try:
            # this import not supported on anything but the Pi
            from picamera import PiCamera

            with PiCamera() as camera:
                LOGGER.info("Capturing image...")
                camera.resolution = (1024, 768)
                camera.start_preview()
                # Camera warm-up time
                time.sleep(2)
                camera.capture("/var/www/html/cam/foo.jpg")
                LOGGER.info("Captured image...")
        except Exception as e:
            LOGGER.error(e)
            return {"error": "Failed taking picture"}, 400

        return {}


class Register(Resource):
    """Registration endpoint

    Arguments:
        Resource {Resource} -- Flask resource

    Returns:
        tuple -- {'message'}, status_code
    """

    def post(self):
        """
        Handle a registration request
        """
        if "email" not in request.get_json():
            return {"error": "Must supply email address"}, 400
        if "password" not in request.get_json():
            return {"error": "Must supply password"}, 400
        if "passwordConfirmation" not in request.get_json():
            return {"error": "Must supply confirmation password"}, 400
        if request.get_json()["password"] != request.get_json()["passwordConfirmation"]:
            return {"error": "Passwords don't match"}, 400
        if len(request.get_json()["password"]) <= PASSWORD_MIN_LEN:
            return (
                {"error": "Password must be > {} characters.".format(PASSWORD_MIN_LEN)},
                400,
            )
        user = db.session.query(User.id).filter_by(email=request.get_json()["email"])
        if user.scalar() is not None:
            return {"error": "Email is already registered."}, 400

        hashed_pw = User.generate_hash(
            plaintext_password=request.get_json()["password"].encode()
        )
        new_user = User(
            email=request.get_json()["email"],
            password=base64.b64encode(hashed_pw).decode(),
        )
        db.session.add(new_user)
        db.session.commit()

        # create tokens
        access_token = create_access_token(identity=new_user.email)
        refresh_token = create_refresh_token(identity=new_user.email)

        # response payload has cookies for the token as well as
        # json payload for metadata so frontend can make use of it
        resp = jsonify({"uid": new_user.id, "email": new_user.email})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp


class Login(Resource):
    """Login endpoint

    Arguments:
        Resource {Resource} -- Flask resource

    Returns:
        tuple -- {'message'}, status_code
    """

    def post(self):
        """
        Handle a login request
        """
        if "email" not in request.json:
            return {"error": "Must supply email address"}, 400
        if "password" not in request.json:
            return {"error": "Must supply password"}, 400

        user = User.query.filter_by(email=request.json["email"]).first()
        if user is None:
            return {"error": "Email or password incorrect"}, 401
        if bcrypt.hashpw(
            request.json["password"].encode(), base64.b64decode(user.password)
        ) != base64.b64decode(user.password):
            return {"error": "Email or password incorrect"}, 401

        # response payload has cookies for the token as well as
        # json payload for metadata so frontend can make use of it
        resp = jsonify({"uid": user.id, "email": user.email})
        access_token = create_access_token(identity=user.email)
        refresh_token = create_refresh_token(identity=user.email)

        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp


class Logout(Resource):
    """Logout endpoint

    Arguments:
        Resource {Resource} -- Flask resource

    Returns:
        tuple -- {'message'}, status_code
    """

    @jwt_required
    def post(self):
        """
        Add the jti to the revoked token table
        """
        jti = get_raw_jwt()["jti"]
        revoked_token = RevokedTokenModel(jti=jti)
        revoked_token.add()
        resp = jsonify({"id": None})
        unset_jwt_cookies(resp)
        return resp


class TokenRefresh(Resource):
    """refresh a token

    Arguments:
        Resource {Resource} -- Flask resource

    Returns:
        tuple -- {'message'}, status_code
    """

    @jwt_refresh_token_required
    def post(self):
        """
        Handle request for new access token
        """
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        # TODO id n/a?
        resp = jsonify({"id": "n/a"})

        set_access_cookies(resp, access_token)
        return resp


@jwt.token_in_blacklist_loader
def TokenCheckBlacklist(decrypted_token):
    """Check if a token is blacklisted

    Arguments:
        Resource {Resource} -- Flask resource

    Returns:
        tuple -- {'message'}, status_code
    """
    jti = decrypted_token["jti"]
    return RevokedTokenModel.is_jti_blacklisted(jti)


@jwt.expired_token_loader
def TokenExpiredCallback(expired_token):
    """Called when a token is expired

    Arguments:
        Resource {Resource} -- Flask resource

    Returns:
        tuple -- {'message'}, status_code
    """
    LOGGER.error("expired token!")
    token_type = expired_token["type"]
    return (
        jsonify(
            {
                "status": 401,
                "sub_status": 42,
                "msg": "The {} token has expired".format(token_type),
            }
        ),
        401,
    )
