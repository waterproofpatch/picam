# standard imports
import threading
import io
import logging
import traceback
import time

# installed imports
import colorlog
from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np
import datetime as dt

HANDLER = colorlog.StreamHandler()
HANDLER.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(filename)s:%(lineno)s:%(message)s"
    )
)
LOGGER = colorlog.getLogger(__name__)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)

GLOBALS = {"output": None, "camera_started": False}


def get_frame():
    """
    Get a single frame from the output.

    :return: None if camera is not started.
    """
    if GLOBALS["camera_started"] == False:
        LOGGER.error("Tried getting a frame before the was started.")
        return None

    with GLOBALS["output"].condition:
        GLOBALS["output"].condition.wait()
        frame = GLOBALS["output"].frame

        # now add timestamp to jpeg
        # Convert to PIL Image
        cv2.CV_LOAD_IMAGE_COLOR = 1  # set flag to 1 to give colour image

        npframe = np.fromstring(frame, dtype=np.uint8)
        pil_frame = cv2.imdecode(npframe, cv2.CV_LOAD_IMAGE_COLOR)

        cv2_im_rgb = cv2.cvtColor(pil_frame, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)

        draw = ImageDraw.Draw(pil_im)

        # Choose a font
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 25)
        myText = "Live stream: " + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Draw the text
        color = "rgb(255,255,255)"

        # get text size
        text_size = font.getsize(myText)

        # set button size + 10px margins
        button_size = (text_size[0] + 20, text_size[1] + 10)

        # create image with correct size and black background
        button_img = Image.new("RGBA", button_size, "black")

        # button_img.putalpha(128)
        # put text on button with 10px margins
        button_draw = ImageDraw.Draw(button_img)
        button_draw.text((10, 5), myText, fill=color, font=font)

        # put button on source image in position (0, 0)
        pil_im.paste(button_img, (0, 0))
        bg_w, bg_h = pil_im.size
        # WeatherSTEM logo in lower left
        size = 64
        # Save the image
        buf = io.BytesIO()
        pil_im.save(buf, format="JPEG")
        frame = buf.getvalue()
    return frame


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


def camera_thread():
    LOGGER.debug("Starting thread...")

    # only available on the pi
    import picamera

    with picamera.PiCamera(resolution="1296x730", framerate=24) as camera:
        GLOBALS["output"] = StreamingOutput()
        camera.start_recording(GLOBALS["output"], format="mjpeg")
        camera.annotate_foreground = picamera.Color(y=0.2, u=0, v=0)
        camera.annotate_background = picamera.Color(y=0.8, u=0, v=0)

        LOGGER.debug("Camera started...")

        # keep the context alive
        while True:
            LOGGER.debug("Sleeping for event...")
            if GLOBALS["sleep_event"].wait(10):
                camera.stop_recording()
                LOGGER.debug("Exiting thread.")
                return


def start_camera_thread():
    """
    Start the camera thread.
    """
    LOGGER.debug("Starting camera...")
    GLOBALS["sleep_event"] = threading.Event()
    GLOBALS["camera_thread"] = threading.Thread(target=camera_thread)
    GLOBALS["camera_thread"].start()
    time.sleep(10)  # camera warm up...
    GLOBALS["camera_started"] = True


def stop_camera_thread():
    """
    Signal and stop the camera thread.
    """
    if "sleep_event" in GLOBALS:
        LOGGER.debug("Signalling thread...")
        GLOBALS["sleep_event"].set()
    if "camera_thread" in GLOBALS:
        LOGGER.debug("Joining thread...")
        GLOBALS["camera_thread"].join()
        LOGGER.debug("Thread joined.")
    LOGGER.debug("Camera thread stopped.")
    GLOBALS["camera_started"] = False


LOGGER.info("Streamer registering shutdown function...")
import atexit

atexit.register(stop_camera_thread)