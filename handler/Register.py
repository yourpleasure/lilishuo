from tornado.web import RequestHandler


class Register(RequestHandler):
    def data_received(self, chunk):
        pass

    async def create_user(self, username, password):
        db = self.application.db
        result = await db.User.insert_one({'_id': username, 'password': password})
        if result is None:


    def get(self):
        self.render(self.settings['static_path'] + u"/html/register.html")

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        result, error_message = self.create_user(username, password)
        if result:
            self.redirect(u"/auth/login/")
        else:
            self.redirect(u"/register")
