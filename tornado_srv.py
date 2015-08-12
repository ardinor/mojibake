#!/opt/mojibake/venv/bin/python

# The below doesn't seem to work from a systemd unit file?
#!/usr/bin/env python

import tornado.web
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import os

from mojibake.main import app
from mojibake.settings import PORT


if __name__ == "__main__":

    app.logger.info('Starting Mojibake...')

    if os.name == 'posix':
        # If we're on Linux, set the process title to mojibake
        import setproctitle
        setproctitle.setproctitle('mojibake')

    container = tornado.wsgi.WSGIContainer(app)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()
