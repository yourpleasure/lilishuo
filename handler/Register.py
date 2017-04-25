from pymongo.errors import DuplicateKeyError
from handler.base import BaseHandler
import re
import logging


class Register(BaseHandler):
    async def create_user(self, username, password):
        db = self.application.db
        result_success = {
            'success': True
        }
        result_fail = {
            'success': False
        }
        try:
            result = await db.User.insert_one({'_id': username, 'password': password})
            if result is None:
                result_fail['message'] = "Create account error"
                return result_fail
            return result_success
        except DuplicateKeyError:
            result_fail['message'] = "Account already exists"
            return result_fail
        except Exception as e:
            logging.exception(e)
            result_fail['message'] = "Server error"
            return result_fail

    def get(self):
        self.render(self.settings['static_path'] + u"/html/register.html")
        return

    async def post(self):
        username = self.get_argument("username", "")
        if not re.match("^[0-9a-zA-Z_@.]+$", username):
            return_data = {
                'result': False,
                'message': "username invalided"
            }
            self.write(return_data)
            self.flush()
            return

        password = self.get_argument("password", "")
        result = await self.create_user(username, password)

        self.write(result)
        self.flush()
