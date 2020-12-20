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
        try:
            font_file = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
            font = ImageFont.truetype(font_file, 25)
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
        except OSError as e:
            LOGGER.error(f"Failed opening fot resource {font_file}")

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
    try:
        import picamera

        with picamera.PiCamera(resolution="1296x730", framerate=24) as camera:
            GLOBALS["output"] = StreamingOutput()
            camera.start_recording(GLOBALS["output"], format="mjpeg")
            camera.annotate_foreground = picamera.Color(y=0.2, u=0, v=0)
            camera.annotate_background = picamera.Color(y=0.8, u=0, v=0)

            LOGGER.debug("Camera started...")
    except ModuleNotFoundError:
        LOGGER.debug("Not running on device, can't import model")

        class FakeCamera:
            def __init__(self):
                self.t = threading.Thread(target=self.record_loop)
                self.do_record = False
                self.output = None

            def record_loop(self):
                LOGGER.debug("Starting record loop...")
                while self.do_record:
                    time.sleep(1)  # wait a bit between each frame
                    LOGGER.debug("fake camera sending frame...")
                    if self.output == None:
                        LOGGER.error("Fake camera output is None...")
                        continue

                    # write a fake frame
                    self.output.write(open("test_images/test_frame_1.jpg", "rb").read())

                LOGGER.debug("Ending record loop.")

            def stop_recording(self):
                LOGGER.debug("Fake camera stopped recording...")
                self.do_record = False
                LOGGER.debug("Waiting for fake camera to shut down...")
                self.t.join()
                LOGGER.debug("Fake camera shut down.")

            def start_recording(self, output):
                LOGGER.debug("Fake camera starting...")
                self.output = output
                self.do_record = True
                self.t.start()

        camera = FakeCamera()
        GLOBALS["output"] = StreamingOutput()
        camera.start_recording(GLOBALS["output"])

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