from handler.base import BaseHandler
from tornado.escape import url_escape


class LoginHandler(BaseHandler):
    def get(self):
        self.render(self.settings['static_path'] + u"/html/login.html")

    async def check_permission(self, username, password):
        db = self.application.db
        try:
            fetch_password = await db.User.find_one({'_id': username}, projection={'password': 1, '_id': 0})
            if fetch_password is None:
                return False, "Account not exists"
            else:
                if fetch_password['password'] == password:
                    return True, "Success"
                else:
                    return False, "Account or Password mismatch"
        except Exception as e:
            print("Exception: {0}".format(e))
            return False, "Server fault"

    async def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth, message = await self.check_permission(username, password)
        if auth:
            self.set_secure_cookie("user", username)
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + url_escape(message)
            self.redirect(u"/auth/login/" + error_msg)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))
