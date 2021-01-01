"""
Views backend. Handles items, logins, registrations, logouts and tokens.
"""
# native imports
import base64
import bcrypt
import os

# flask imports
from flask import jsonify, send_from_directory, Response
from flask_restful import Resource, request
from sqlalchemy import desc
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

# my imports, from __init__
from backend import jwt, db, flask_app, stream, utils
from backend.models import User, Image, RevokedTokenModel
from backend.logger import LOGGER

GLOBALS = {"camera": stream.Camera()}


@flask_app.route("/api/stream.mjpg")
def live_stream():
    return Response(
        utils.generate_live_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@flask_app.route("/test_images/<path:path>")
def send_images(path):
    """
    Image file resolution for development
    """
    return send_from_directory("../test_images", path)


class Images(Resource):
    """
    Images endpoint

    Arguments:
        Resource {Resource} - Flask resource

    Returns:
        tuple - {'message'}, status_code
    """

    @jwt_required
    def get(self):
        """
        Handle a get request for all files
        """
        return [x.as_json() for x in Image.query.order_by(desc(Image.id)).all()]

    @jwt_required
    def post(self):
        """
        Start the camera and take a picture.
        """
        LOGGER.debug("starting capture...")
        if not GLOBALS["camera"].take_picture(flask_app):
            return {"error": "Failed taking picture"}, 400

        return [x.as_json() for x in Image.query.order_by(desc(Image.id)).all()]


class DeleteImage(Resource):
    """
    Access a single image by its ID
    """

    @jwt_required
    def delete(self, id):
        """
        Delete an image
        """
        LOGGER.debug(f"Delete request for {id}")

        # remove from disk
        if flask_app.debug:
            path = Image.query.filter_by(id=id).first().url
        else:
            path = os.path.join(
                "/var/www/html/cam/", Image.query.filter_by(id=id).first().url
            )
        LOGGER.debug(f"removing {path}")
        os.remove(path)

        Image.query.filter_by(id=id).delete()
        db.session.commit()
        return [x.as_json() for x in Image.query.order_by(desc(Image.id)).all()]


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
        access_token = create_access_token(
            identity={"email": user.email, "uid": user.id}
        )
        refresh_token = create_refresh_token(
            identity={"email": user.email, "uid": user.id}
        )

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
        resp = jsonify({"uid": None})
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
        LOGGER.debug("Getting new non-fresh access token")
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)
        resp = jsonify({"uid": current_user["uid"], "email": current_user["email"]})
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
    return (
        jsonify({}),
        402,
    )
