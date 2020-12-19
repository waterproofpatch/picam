# standard imports
import threading
import io
import logging
import socketserver
import traceback
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# listen to this port for connections
LISTEN_PORT = 4444

PAGE = """\
<html>
<head>
<title>MJPEG streaming</title>
</head>
<body>
<h1>Stream</h1>
<img src="stream.mjpg" width="1296" height="730" />
</body>
</html>
"""

GLOBALS = {"output": None}


def get_frame():
    """
    Get a single frame from the output.
    """
    if GLOBALS["output"] is None:
        LOGGER.error(
            "GLOBALS output is None, this could mean camera hasn's started output"
        )
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


class StreamingServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()

        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == "/stream.mjpg":
            headers = {
                "Age": 0,
                "Cache-Control": "no-cache, private",
                "Pragma": "no-cache",
                "Content-Type": "multipart/x-mixed-replace; boundary=FRAME",
            }
            self.send_response(200)

            for header in headers:
                self.send_header(header, headers[header])

            self.end_headers()
            try:
                while True:
                    frame = get_frame()
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                traceback.print_exc()
                logging.warning(
                    "Removed streaming client %s: %s", self.client_address, str(e)
                )
        else:
            self.send_error(404)
            self.end_headers()


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


def start_server():
    """
    Start the server. Does not return.
    """
    address = ("", LISTEN_PORT)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()


if __name__ == "__main__":
    start_camera_thread()
    try:
        LOGGER.debug(f"Starting server on {LISTEN_PORT}")
        start_server()
    finally:
        stop_camera_thread()
        LOGGER.debug("Threads joined. Exiting.")
