from tornado.websocket import WebSocketHandler
import json
import logging


class BaseWebSocketHandler(WebSocketHandler):
    def on_message(self, message):
        pass

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user is None:
            return None
        return user.decode()


class InfoHandler(BaseWebSocketHandler):
    clients = {}

    async def open(self):
        user = self.get_secure_cookie("user").decode()
        if not user:
            self.close()
        else:
            if user not in InfoHandler.clients:
                InfoHandler.clients[user] = self
            elif InfoHandler.clients[user] != self:
                message = {
                    'type': 'control',
                    'data': "Already Login"
                }
                self.write_message(message)

    @staticmethod
    async def check_alive(user_id):
        if user_id in InfoHandler.clients:
            return True
        return False

    async def close_connect(self, info):
        user = self.get_current_user()
        if user is None:
            self.close()
        else:
            if user in self.clients:
                del self.clients[user]
        return

    async def handle_get_all(self, info):
        username = self.get_current_user()
        if username is None:
            self.close()
            return

        result = {
            'type': 'send_all',
            'data': {},
            'success': True
        }
        db = self.application.db
        try:
            data = await db.User.find_one({'_id': username}, projection={'_id': 0, 'friend_list': 1, 'unread': 1})
            result['data']['friend_list'] = sorted(data.get('friend_list', []))
            unread = data.get('unread', None)
            if unread is not None:
                result['data']['friend_request'] = unread.get('friend_request', [])
                result['data']['unread_message_number'] = unread.get('unread_message_number', {})
            self.write_message(result)
        except Exception as e:
            logging.exception(e)
            del result['data']
            result['success'] = False
            result['message'] = "Server Error"
            self.write_message(result)

        return

    async def on_message(self, message):
        handler = {
            'close': self.close_connect
        }
        try:
            message_dict = json.loads(message)
            await handler[message_dict['type']](message_dict['data'])
        except Exception as e:
            logging.exception(e)
        return
