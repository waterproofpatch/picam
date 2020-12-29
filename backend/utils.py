# native imports
import uuid
import shutil
import time

# my imports, from __init__
from backend import LOGGER, stream, flask_app, db
from backend.models import Image


# path to a test image for use with development
TEST_SRC_IMAGE_PATH = "test_images/test_image.jpg"


def generate_live_stream():
    # get camera frame
    LOGGER.info("Starting camera output...")
    camera = stream.Camera()
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