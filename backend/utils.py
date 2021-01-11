"""
Utilities
"""
# standard imports

# project imports
from backend.logger import LOGGER


def generate_live_stream(camera):
    """
    Handle the creation of the live stream.
    """
    LOGGER.info("Starting camera output...")
    camera.start()
    LOGGER.info("Camera output started...")
    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                LOGGER.error("Failed getting frame.")
                camera.stop()
                return "Error getting stream."
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
    finally:
        LOGGER.info("Stopping camera output...")
        camera.stop()
        LOGGER.info("Camera output stopped...")
