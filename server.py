from tornado.web import Application, url, RequestHandler, StaticFileHandler, authenticated
from conf.Settings import settings
from tornado.ioloop import IOLoop
from tornado.escape import xhtml_escape
from handler.Auth import LoginHandler, LogoutHandler
from handler.Register import Register
import os
public_root = os.path.join(os.path.dirname(__file__), 'static')


class MainHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    @authenticated
    def get(self):
        username = xhtml_escape(self.current_user)
        self.render(public_root + "/html/index.html", username=username)


def make_app():
    return Application([
        url(r"/", MainHandler),
        url(r"/auth/login/", LoginHandler),
        url(r"/auth/logout/", LogoutHandler),
        url(r"/register", Register),
        url(r"/static/(.*)", StaticFileHandler, dict(path=settings['static_path']))
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888, "127.0.0.1")
    IOLoop.current().start()
