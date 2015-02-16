import tornado.web
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import os

from mojibake.main import app
from mojibake.settings import PORT, DEBUG, LOG_DIR


if __name__ == "__main__":

    app.logger.info('Starting Mojibake...')

    if os.name == 'posix':
        import setproctitle
        setproctitle.setproctitle('mojibake')  # Set the process title to mojibake

    container = tornado.wsgi.WSGIContainer(app)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()
