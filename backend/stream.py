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
        "%(asctime)s:%(log_color)s%(levelname)s:%(filename)s:%(lineno)s:%(message)s"
    )
)
LOGGER = colorlog.getLogger(__name__)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)


class Camera:
    def __init__(self):
        self.camera_started = False
        self.output = StreamingOutput()
        self.event = threading.Event()
        self.camera_thread = threading.Thread(target=self.camera_thread)

    def start(self):
        LOGGER.debug("Starting camera...")
        self.camera_thread.start()
        LOGGER.info("Waiting 10 seconds for camera to start...")
        time.sleep(10)  # camera warm up...
        self.camera_started = True

    def stop(self):
        LOGGER.debug("Signalling thread...")
        self.event.set()
        LOGGER.debug("Joining thread...")
        self.camera_thread.join()
        LOGGER.debug("Camera thread joined.")
        self.camera_started = False

    def get_frame(self):
        """
        Get a single frame from the output.

        :return: None if camera is not started.
        """
        if not self.camera_started:
            LOGGER.error("Tried getting a frame before the was started.")
            return None

        with self.output.condition:
            LOGGER.debug("Waiting for output condition...")
            self.output.condition.wait()
            LOGGER.debug("Got output condition...")
            frame = self.output.frame

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
                timestamp_text = "Live stream: " + dt.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Draw the text
                color = "rgb(255,255,255)"

                # get text size
                text_size = font.getsize(timestamp_text)

                # set button size + 10px margins
                button_size = (text_size[0] + 20, text_size[1] + 10)

                # create image with correct size and black background
                button_img = Image.new("RGBA", button_size, "black")

                # button_img.putalpha(128)
                # put text on button with 10px margins
                button_draw = ImageDraw.Draw(button_img)
                button_draw.text((10, 5), timestamp_text, fill=color, font=font)

                # put button on source image in position (0, 0)
                pil_im.paste(button_img, (0, 0))
            except OSError as _:
                LOGGER.error(f"Failed opening fot resource {font_file}")

            # Save the image
            buf = io.BytesIO()
            pil_im.save(buf, format="JPEG")
            frame = buf.getvalue()

        return frame

    def camera_thread(self):
        LOGGER.debug("Starting thread...")

        # only available on the pi
        try:
            import picamera

            with picamera.PiCamera(resolution="1296x730", framerate=24) as camera:
                camera.start_recording(self.output, format="mjpeg")
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
                    last_index = 1

                    while self.do_record:

                        # wait a bit between each frame
                        time.sleep(1)

                        LOGGER.debug("fake camera sending frame...")
                        if self.output == None:
                            LOGGER.error("Fake camera output is None...")
                            continue

                        # write a fake frame
                        if last_index == 1:
                            last_index = 2
                            self.output.write(
                                open("test_images/test_frame_2.jpg", "rb").read()
                            )
                        else:
                            last_index = 1
                            self.output.write(
                                open("test_images/test_frame_1.jpg", "rb").read()
                            )

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
            camera.start_recording(self.output)

        # keep the context alive
        while True:
            LOGGER.debug("Sleeping for event...")
            if self.event.wait(10):
                LOGGER.info("Thread was signalled, stopping...")
                camera.stop_recording()
                LOGGER.debug("Exiting thread.")
                return


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