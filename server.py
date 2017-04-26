import tornado
from tornado.web import url, StaticFileHandler, authenticated
from tornado.httpserver import HTTPServer
from conf.Settings import settings
from tornado.ioloop import IOLoop
from tornado.escape import xhtml_escape
from handler.Auth import LoginHandler, LogoutHandler
from api.Init import InitHandler
from api.User import UserHandler
from api.Message import MessageHandler
from handler.Register import Register
from handler.base import BaseHandler
from handler.InfoHandler import InfoHandler
from motor.motor_tornado import MotorClient
from tornado.options import define, options
import sys

define("mongo_conf", type=dict)
define('log_file_prefix', default='/tmp/test.log')
define('log_rotate_mode', default='time')
define('log_rotate_when', default='M')
define('log_rotate_interval', default=1)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            url(r"/", MainHandler),
            url(r"/auth/login/", LoginHandler),
            url(r"/auth/logout/", LogoutHandler),
            url(r"/register", Register),
            url(r"/api/init/", InitHandler),
            url(r"/api/user/", UserHandler),
            url(r"/api/message/(.*)/(history)?", MessageHandler),
            url(r"/api/message/", MessageHandler),
            url(r"/websocket", InfoHandler),
            url(r"/static/(.*)", StaticFileHandler, dict(path=settings['static_path']))
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = MotorClient(mongo_conf['url'])[mongo_conf['database']]


class MainHandler(BaseHandler):
    @authenticated
    def get(self):
        username = xhtml_escape(self.current_user)
        self.render(self.settings['static_path'] + "/html/index.html", username=username)


if __name__ == "__main__":
    if sys.version_info[0] != 3 or sys.version_info[1] < 5:
        print("This script requires Python version >= 3.5")
        sys.exit(1)

    options.parse_config_file("conf/DBconf.py")
    mongo_conf = options.mongo_conf
    http_server = HTTPServer(Application())
    http_server.listen(8888)
    IOLoop.instance().start()
