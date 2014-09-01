import tornado.web
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import os

from mojibake.main import app
from mojibake.settings import PORT

if os.name == 'posix':
    import setproctitle
    setproctitle.setproctitle('mojibake')  # Set the process title to mojibake

print('Starting Mojibake...')
container = tornado.wsgi.WSGIContainer(app)
http_server = tornado.httpserver.HTTPServer(container)
http_server.listen(PORT)
tornado.ioloop.IOLoop.instance().start()
