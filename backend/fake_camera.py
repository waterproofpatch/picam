"""
Implementation for the stream.
"""

# standard imports
import threading
import time

# installed imports

# project imports
from backend.logger import LOGGER


class FakeCamera:
    """
    Fake camera object for testing on laptop.
    """

    def __init__(self):
        self.record_loop_thread = threading.Thread(target=self.record_loop)
        self.do_record = False
        self.output = None

    def record_loop(self):
        """
        Fake camera recording loop
        """
        LOGGER.debug("Starting record loop...")
        last_index = 1

        while self.do_record:

            # wait a bit between each frame
            time.sleep(1)

            LOGGER.debug("fake camera sending frame...")
            if self.output is None:
                LOGGER.error("Fake camera output is None...")
                continue

            # write a fake frame
            if last_index == 1:
                last_index = 2
                self.output.write(open("test_images/test_frame_2.jpg", "rb").read())
            else:
                last_index = 1
                self.output.write(open("test_images/test_frame_1.jpg", "rb").read())

        LOGGER.debug("Ending record loop.")

    def stop_recording(self):
        """
        Stop the fake camera recording thread.
        """
        LOGGER.debug("Fake camera stopped recording...")
        self.do_record = False
        LOGGER.debug("Waiting for fake camera to shut down...")
        self.record_loop_thread.join()
        LOGGER.debug("Fake camera shut down.")

    def start_recording(self, output):
        """
        Start the fake camera recording thread
        """
        LOGGER.debug("Fake camera starting...")
        self.output = output
        self.do_record = True
        self.record_loop_thread.start()
