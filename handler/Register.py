from tornado.web import RequestHandler
import os
public_root = os.path.join(os.path.dirname(__file__), '../static')


class Register(RequestHandler):
    def data_received(self, chunk):
        pass

    @staticmethod
    def create_user(username, password):
        print(username, password)
        return True, None

    def get(self):
        self.render(public_root + u"/html/register.html")

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        result, error_message = self.create_user(username, password)
        if result:
            self.redirect(u"/auth/login/")
        else:
            self.redirect(u"/register")
