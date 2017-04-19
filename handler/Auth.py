from handler.base import BaseHandler
from tornado.escape import json_encode, url_escape
from tornado.gen import coroutine


class LoginHandler(BaseHandler):
    def get(self):
        self.render(self.settings['static_path'] + u"/html/login.html")

    @staticmethod
    def check_permission(username, password):
        if username == "admin" and password == "admin":
            return True
        return False

    @coroutine
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
