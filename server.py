import tornado
from tornado.web import url, RequestHandler, StaticFileHandler, authenticated
from tornado.httpserver import HTTPServer
from conf.Settings import settings
from tornado.ioloop import IOLoop
from tornado.escape import xhtml_escape
from handler.Auth import LoginHandler, LogoutHandler
from handler.Register import Register
from handler.base import BaseHandler
import os
from motor.motor_tornado import MotorClient
from tornado.options import define, options

define("mongo_conf", type=dict)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            url(r"/", MainHandler),
            url(r"/auth/login/", LoginHandler),
            url(r"/auth/logout/", LogoutHandler),
            url(r"/register", Register),
            url(r"/static/(.*)", StaticFileHandler, dict(path=settings['static_path']))
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = MotorClient(config['url'])[config['database']]


class MainHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @authenticated
    def get(self):
        username = xhtml_escape(self.current_user)
        self.render(self.settings['static_path'] + "/html/index.html", username=username)


if __name__ == "__main__":
    options.parse_config_file("conf/DBconf.py")
    config = options.mongo_conf
    http_server = HTTPServer(Application())
    http_server.listen(8888, "127.0.0.1")
    IOLoop.instance().start()
