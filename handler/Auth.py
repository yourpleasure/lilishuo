from tornado.web import RequestHandler
from tornado.escape import json_encode, url_escape
import os
public_root = os.path.join(os.path.dirname(__file__), '../static')


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get_current_user(self):
        return self.get_secure_cookie("user")


class LoginHandler(BaseHandler):
    def get(self):
        self.render(public_root + u"/html/login.html")

    @staticmethod
    def check_permission(username, password):
        if username == "admin" and password == "admin":
            return True
        return False

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(username, password)
        if auth:
            self.set_secure_cookie("user", json_encode(username))
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + url_escape("Login incorrect")
            self.redirect(u"/auth/login/" + error_msg)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
