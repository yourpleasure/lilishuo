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
            if result1 is None \
                or result1.get('unread') is None \
                    or result1['unread'].get('message') is None \
                    or result1['unread']['message'].get(friend_id) is None:
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
    async def fetch_history_message(self, username, friend_id, message_index):
        db = self.application.db
        result_success = {
            "success": True,
            "data": []
        }
        result_fail = {
            "success": False
        }
        if message_index == -1:
            try:
                all_messages = await db.User.find_one(
                    {"_id": username},
                    projection={'_id': 0, "message." + friend_id: 1}
                )
                if all_messages is None:
                    result_fail['message'] = "Unknown error"
                    return result_fail
                else:
                    if all_messages.get("message") is None or all_messages['message'].get(friend_id) is None:
                        message_index = 0
                        message_data = []
                    else:
                        real_message = all_messages['message'][friend_id]
                        message_number = len(real_message)
                        if message_number >= 30:
                            message_index = message_number - 30
                            message_data = real_message[message_index - 30:]
                        else:
                            message_index = 0
                            message_data = real_message
                    result_success['index'] = message_index
                    result_success['data'] = message_data
                    return result_success
            except Exception as e:
                print("Exception: {0}".format(e))
                result_fail['message'] = "Server error"
                return result_fail
        else:
            try:
                if message_index >= 30:
                    fetch_number = 30
                    message_index -= fetch_number
                else:
                    fetch_number = message_index
                    message_index = 0
                messages = await db.User.find_one(
                    {'_id': username},
                    projection={'_id': 0, "message." + friend_id: {"$slice": [message_index, fetch_number]}}
                )
                if messages is None or messages.get('message') is None or messages['message'].get('friend') is None:
                    result_fail['message'] = "Unknown error"
                    return result_fail
                else:
                    result_success['data'] = messages['message'][friend_id]
                    result_success['index'] = message_index
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
            message_index = self.get_query_argument("index")
            try:
                message_index = int(message_index)
            except Exception as e:
                print("Exception: {0}".format(e))
                result_fail['message'] = "unsupported query value"
                self.write(result_fail)
                self.flush()
                return
            if message_index is None or message_index == 0:
                result_fail['message'] = "Unsupported parameter or unsupported value"
                self.write(result_fail)
                self.flush()
                return

            result = await self.fetch_history_message(username, friend_id, message_index)
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

    @authenticated
    async def delete_message(self, username, friend_id, message_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            result = await db.User.find_one_and_update(
                {"_id": username},
                {"$pull": {"message." + friend_id: message_id}},
                projection=({"_id": 1})
            )
            if result is not None:
                return result_success
            else:
                result_fail['message'] = "Unknown error"
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"

        return result_fail

    @authenticated
    async def delete(self, *args):
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
        message_id = self.get_query_argument("message_id")
        if friend_id is None or message_id is None:
            result_fail['message'] = "Parameter error"
            return result_fail

        result = await self.delete_message(username, friend_id, message_id)
        self.write(result)
        self.flush()
        return
