# native imports
import uuid
import shutil
import time

# my imports, from __init__
from backend import stream, flask_app, db
from backend.models import Image
from backend.logger import LOGGER


GLOBALS = {"camera": None}


def generate_live_stream():
    LOGGER.info(f"Starting camera output...")
    GLOBALS["camera"] = stream.Camera()
    GLOBALS["camera"].start()
    LOGGER.info("Camera output started...")
    try:
        while True:
            frame = GLOBALS["camera"].get_frame()
            if frame is None:
                LOGGER.error("Failed getting frame.")
                GLOBALS["camera"].stop()
                return "Error getting stream."
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
    finally:
        LOGGER.info("Stopping camera output...")
        GLOBALS["camera"].stop()
        LOGGER.info("Camera output stopped...")
