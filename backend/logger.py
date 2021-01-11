"""
Control logging formatting.
"""
# standard imports
import logging

# installed imports
import colorlog

# get a logger for use everywhere
HANDLER = colorlog.StreamHandler()
HANDLER.setFormatter(
    colorlog.ColoredFormatter(
        "%(asctime)s:%(log_color)s%(levelname)s:%(filename)s:%(lineno)s:%(message)s"
    ),
)

LOGGER = colorlog.getLogger(__name__)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)
