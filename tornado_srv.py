import tornado.web
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import os

import logging
from logging.handlers import TimedRotatingFileHandler

from mojibake.main import app
from mojibake.settings import PORT, DEBUG, LOG_DIR


def prepare_logging():

    logger = logging.getLogger('mojibake')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    if DEBUG:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    logger.addHandler(handler)

    # Set the size limit to 5~mb
    file_handler = TimedRotatingFileHandler(os.path.join(LOG_DIR, 'mojibake.log'), when="D", backupCount=7)
    file_formatter = logging.Formatter("""
Time: %(asctime)s
Level: %(levelname)s
Method: %(method)s
Path: %(url)s
IP: %(ip)s
Message: %(message)s
-------------
""")

    if DEBUG:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


if __name__ == "__main__":

    prepare_logging()
    logger = logging.getLogger('mojibake')

    if os.name == 'posix':
        import setproctitle
        setproctitle.setproctitle('mojibake')  # Set the process title to mojibake

    logger.info('Starting Mojibake...')
    container = tornado.wsgi.WSGIContainer(app)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()
