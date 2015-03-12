import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os

from mojibake.settings import DEBUG, LOG_DIR

formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setFormatter(formatter)
if DEBUG:
    stream_handler.setLevel(logging.DEBUG)
else:
    stream_handler.setLevel(logging.INFO)

# Set the size limit to 5~mb
# file_handler = TimedRotatingFileHandler(os.path.join(LOG_DIR, 'mojibake.log'), when="D", backupCount=7)
# file_formatter = logging.Formatter("""
# Time: %(asctime)s
# Level: %(levelname)s
# Method: %(method)s
# Path: %(url)s
# IP: %(ip)s
# Message: %(message)s
# -------------
# """)

# if DEBUG:
#     file_handler.setLevel(logging.DEBUG)
# else:
#     file_handler.setLevel(logging.WARNING)
# file_handler.setFormatter(file_formatter)
