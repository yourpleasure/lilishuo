from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def check_user_exists(self, username):
        db = self.application.db
        if db.User.find({'_id': username}, projection={'_id': 1}).count() > 0:
            return True
        return False
