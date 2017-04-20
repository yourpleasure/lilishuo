from pymongo.errors import DuplicateKeyError
from tornado.web import RequestHandler


class Register(RequestHandler):
    def data_received(self, chunk):
        pass

    async def create_user(self, username, password):
        db = self.application.db
        try:
            result = await db.User.insert_one({'_id': username, 'password': password})
            if result is None:
                return False, "Create account error"
            return True, "success"
        except DuplicateKeyError:
            return False, "Account already exists"
        except Exception as e:
            return False, "{0}".format(e)

    def get(self):
        self.render(self.settings['static_path'] + u"/html/register.html")

    async def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        result, error_message = await self.create_user(username, password)
        return_data = {
            'result': result,
            'message': error_message
        }

        self.write(return_data)
        self.flush()
