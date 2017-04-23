from tornado.web import authenticated
from handler.base import BaseHandler
from handler.InfoHandler import InfoHandler
from tornado.escape import json_decode


class MessageHandler(BaseHandler):
    @authenticated
    async def fetch_message(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            result1 = await db.User.find_one(
                {'_id': username},
                projection={'unread.message.' + friend_id: 1}
            )
            try:
                message = result1['unread']['message'][friend_id]
            except Exception as e:
                print("Exception: {0}".format(e))
                result_fail['message'] = "Server error"
                return result_fail

            result2 = await db.User.find_one_and_update(
                {'_id': friend_id},
                {'$push': {'message.'+friend_id: {"$each": message}}},
                projection={'_id': 1}
            )
            if result2 is None:
                result_fail['message'] = "Get unread message failed"
                return result_fail
            result_success['data'] = message
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def get(self):
        username = self.get_current_user()
        result_fail = {
            'success': False
        }
        if username is None:
            result_fail['message'] = 'Unknown User'
            self.write(result_fail)
            self.flush()
            return

        data = json_decode(self.request.body)
        friend_id = data.get('friend_id', None)
        result = await self.check_id_in_friend_list(username, friend_id)
        if not result['success']:
            self.write(result)
            self.flush()
            return

        result = await self.fetch_message(username, friend_id)
        self.write(result)
        self.flush()
        return

    @authenticated
    async def update_message(self, username, data):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        message = data.get('message', None)
        friend_id = data.get('friend_id', None)
        timestamp = data.get('timestamp', None)
        message_id = str(timestamp) + '_' + username
        if message is None or friend_id is None or timestamp is None:
            result_fail['message'] = "Message format error"
            return result_fail
        try:
            result1 = await db.User.find_one_and_update(
                {'_id': username},
                {'$push': {'message.'+friend_id: {message_id: message}}},
                projection={'_id': 1}
            )
            result2 = await db.User.find_one_and_update(
                {'_id': friend_id},
                {'$push': {'unread.message.'+username: {message_id: message}}, '$inc': {'unread.unread_message_numbers.'+username: 1}},
                projection={'_id': 1}
            )
            if result1 is None or result2 is None:
                result_fail['message'] = "Send message failed"
                return result_fail
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def post(self):
        username = self.get_current_user()
        result_fail = {
            'success': False
        }
        if username is None:
            result_fail['message'] = 'Unknown User'
            self.write(result_fail)
            self.flush()
            return

        data = json_decode(self.request.body)
        friend_id = data.get('friend_id', None)
        result = await self.check_id_in_friend_list(username, friend_id)
        if not result['success']:
            self.write(result)
            self.flush()
            return

        result = await self.update_message(username, data)
        if result['success']:
            if friend_id in InfoHandler.clients:
                destination = InfoHandler.clients[friend_id]
                message = {
                    'type': "send_message",
                    'data': username
                }
                try:
                    destination.write_message(message)
                except Exception as e:
                    print("Exception: {0}".format(e))
        self.write(result)
        self.flush()
        return


    def delete(self):
        pass
