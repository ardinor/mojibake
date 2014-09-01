import tornado.web
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop

from mojibake.main import app
from mojibake.settings import PORT

container = tornado.wsgi.WSGIContainer(app)
http_server = tornado.httpserver.HTTPServer(container)
http_server.listen(PORT)
tornado.ioloop.IOLoop.instance().start()
