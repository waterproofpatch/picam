"""
Views backend. Handles items, logins, registrations, logouts and tokens.
"""
# native imports
import base64
import shutil
import bcrypt
import os
import time
import uuid

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
from backend import jwt, db, flask_app, allowed_file, LOGGER, stream
from backend.models import User, Image, RevokedTokenModel

# globals
PASSWORD_MIN_LEN = 13

# path to a test image for use with development
TEST_SRC_IMAGE_PATH = "test_images/test_image.jpg"


def generate_live_stream():
    # get camera frame
    LOGGER.info("Starting camera output...")
    stream.start_camera_thread()
    LOGGER.info("Camera output started...")
    try:
        while True:
            frame = stream.get_frame()
            if frame is None:
                LOGGER.error("Failed getting frame.")
                stream.stop_camera_thread()
                return "Error getting stream."
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
    finally:
        LOGGER.info("Stopping camera output...")
        stream.stop_camera_thread()
        LOGGER.info("Camera output stopped...")


@flask_app.route("/api/stream.mjpg")
def live_stream():
    return Response(
        generate_live_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@flask_app.route("/test_images/<path:path>")
def send_images(path):
    """
    Image file resolution for development
    """
    LOGGER.debug("sending file")
    return send_from_directory("../test_images", path)


def take_picture():
    """
    Take a picture (or return static, if not connected to camera).
    :return: True if taking a picture was successful.
    "return: False if taking a picture failed.
    """
    img_uuid = uuid.uuid4()

    # debugging without a camera means faking an image capture. Achieve this by
    # copying a pre-existing image and naming it uniquely.
    if flask_app.debug:
        shutil.copyfile(TEST_SRC_IMAGE_PATH, f"test_images/{img_uuid}.jpg")
        image = Image(url=f"test_images/{img_uuid}.jpg")
        db.session.add(image)
        db.session.commit()
        return True

    # if we're not debugging, try and capture an image from the actual camera.
    try:
        # this import not supported on anything but the Pi
        from picamera import PiCamera

        with PiCamera() as camera:
            LOGGER.info("Capturing image...")
            camera.resolution = (1024, 768)
            camera.start_preview()

            # Camera warm-up time
            time.sleep(2)

            # /var/www/html/cam is writable by 'pi', and nginx
            # routes the requests for /cam/ to this location.
            path = f"/var/www/html/cam/{img_uuid}.jpg"
            camera.capture(path)

            # store a link to it in the database
            LOGGER.info(f"Captured image, saved to path {path}, updating db...")

            # nginx routes *.jpg requests appropriately
            image = Image(url=f"{img_uuid}.jpg")
            db.session.add(image)
            db.session.commit()

            LOGGER.info("Done capturing image...")
            return True
    except Exception as e:
        LOGGER.error(e)
        return False


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
        if not take_picture():
            return {"error": "Failed taking picture"}, 400

        return [x.as_json() for x in Image.query.order_by(desc(Image.id)).all()]


class _Image(Resource):
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
        401,
    )
