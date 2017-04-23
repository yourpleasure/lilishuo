from tornado.web import authenticated
from handler.base import BaseHandler
from handler.InfoHandler import InfoHandler
from tornado.escape import json_decode


class MessageHandler(BaseHandler):
    @authenticated
    async def fetch_unread_message(self, username, friend_id):
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
            # noinspection PyBroadException
            try:
                message = result1['unread']['message'][friend_id]
            except Exception:
                result_success['data'] = []
                return result_success

            result2 = await db.User.find_one_and_update(
                {'_id': username},
                {'$push': {'message.'+friend_id: {"$each": message}},
                 "$unset": {'unread.message.' + friend_id: ""},
                 "$set": {"unread.unread_message_numbers."+friend_id: 0}},
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
    async def fetch_history_message(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True,
            "data": []
        }
        result_fail = {
            "success": False
        }
        try:
            result1 = await db.User.find_one(
                {'_id': username},
                projection={'index.' + friend_id: 1}
            )
            # noinspection PyBroadException
            try:
                index = result1['index'][friend_id]
            except Exception:
                all_message = await db.User.find_one(
                    {'_id': username},
                    projection={'message.' + friend_id: 1}
                )
                # noinspection PyBroadException
                try:
                    messages = all_message['message'][friend_id]
                except Exception:
                    return result_success
                index = len(messages)
                index -= 30
                if index < 0:
                    index = 0
                try:
                    await db.User.find_one_and_update(
                        {'_id': username},
                        {"$set": {"index.'" + friend_id+ "'": index}},
                        projection={'_id': 1}
                    )
                except Exception as e:
                    print("Exception: {0}".format(e))
                result_success['data'] = messages[-30:]
                return result_success

            if index == 0:
                return result_success
            else:
                index -= 30
                if index < 0:
                    number = 30 + index
                    index = 0
                else:
                    number = 30
            result2 = await db.User.find_one(
                {'_id': username},
                projection={'message.' + friend_id: {"$slice": [index, number]}}
            )
            try:
                messages = result2['message'][friend_id]
            except Exception as e:
                print("Exception: {0}".format(e))
                result_fail['message'] = "Unknown error"
                return result_fail
            result_success['data'] = messages
            try:
                await db.User.find_one_and_update(
                    {'_id': username},
                    {"$set": {"index." + friend_id: index}},
                    projection={'_id': 1}
                )
            except Exception as e:
                print("Exception: {0}".format(e))
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def get(self, *args):
        username = self.get_current_user()
        result_fail = {
            'success': False
        }
        if username is None:
            result_fail['message'] = 'Unknown User'
            self.write(result_fail)
            self.flush()
            return

        if len(args) != 2:
            result_fail['message'] = "Url error"
            self.write(result_fail)
            self.flush()
            return

        friend_id = args[0]
        result = await self.check_id_in_friend_list(username, friend_id)
        if not result['success']:
            self.write(result)
            self.flush()
            return

        if args[1] is None:
            result = await self.fetch_unread_message(username, friend_id)
            self.write(result)
            self.flush()
            return
        elif args[1] == "history":
            result = await self.fetch_history_message(username, friend_id)
            self.write(result)
            self.flush()
            return
        else:
            result_fail['message'] = "Unsupported parameter"
            self.write(result_fail)
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
                {'$push': {'unread.message.'+username: {message_id: message}},
                 '$inc': {'unread.unread_message_numbers.'+username: 1}},
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
    async def post(self, *args):
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

    def delete(self, *args):
        pass
