from tornado.websocket import WebSocketHandler
import json


class BaseWebSocketHandler(WebSocketHandler):
    def on_message(self, message):
        pass

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user is None:
            return None
        return user.decode()

    async def check_user_exists(self, username):
        db = self.application.db
        result = {
            "err_code": 0,
            "result": True
        }
        try:
            count = await db.User.find({'_id': username}, projection={'_id': 1}).count()
            if count == 0:
                result['result'] = False
                result['message'] = "User not exists"
        except Exception as e:
            print("Exception: {0}".format(e))
            result['err_code'] = 1
            result['result'] = False
            result['message'] = "Server error"
        finally:
            return result

    async def check_id_in_friend_list(self, username, friend_id):
        db = self.application.db
        result = {
            "err_code": 0,
            "result": True
        }
        try:
            exist = await db.User.find_one({'_id': username, 'friendlist': {'$elemMatch': {"$eq": friend_id}}})
            if exist is None:
                result['result'] = False
            else:
                result['message'] = "Already in friend_list"
        except Exception as e:
            print("Exception: {0}".format(e))
            result['err_code'] = 1
            result['message'] = "Server Error"
        finally:
            return result

    async def add_friend(self, username, friend_id):
        db = self.application.db
        result = {
            'err_code': 0,
            'result': True
        }
        try:
            update = await db.User.find_one_and_update({'_id': username}, {'$addToSet': {'friendlist': friend_id}})
            if update is None:
                result['result'] = False
        except Exception as e:
            print("Exception: {0}".format(e))
            result['err_code'] = 1
            result['result'] = False
            result['message'] = "Server Error"
        finally:
            return result

    async def delete_friend(self, username, friend_id):
        db = self.application.db
        result = {
            'err_code': 0,
            'result': True
        }
        try:
            update = await db.User.find_one_and_update({'_id': username}, {'$pull': {'friendlist': friend_id}})
            if update is None:
                result['result'] = False
        except Exception as e:
            print("Exception: {0}".format(e))
            result['err_code'] = 1
            result['result'] = False
            result['message'] = "Server Error"
        finally:
            return result


class InfoHandler(BaseWebSocketHandler):
    clients = {}

    def open(self):
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

    async def handle_add_friend_request(self, friend_id):
        error_send_message = {
            'type': 'add_friend_failed',
            'data': {
                'err_code': 1,
                'result': False,
                'message': 'Server error'
            }
        }
        user = self.get_current_user()
        if user is None:
            self.close()
            return
        if user == friend_id:
            error_send_message['data']['message'] = "Can't add yourself"
            self.write_message(error_send_message)
            return

        result = await self.check_user_exists(friend_id)
        if result['err_code'] != 0:
            try:
                self.write_message(error_send_message)
            except Exception as e:
                print("Exception: {0}".format(e))
            return

        if result['result']:
            exist = await self.check_id_in_friend_list(user, friend_id)
            if exist['err_code'] != 0:
                try:
                    self.write_message(error_send_message)
                except Exception as e:
                    print("Exception: {0}".format(e))
                return

            if exist['result']:
                send_message = {
                    'type': 'add_friend_failed',
                    'data': {
                        'err_code': 1,
                        'result': False,
                        'message': exist['message']
                    }
                }
                try:
                    self.write_message(send_message)
                except Exception as e:
                    print("Exception: {0}".format(e))
                return
            else:
                if self.check_alive(friend_id):
                    send_message = {
                        'type': 'add_friend_request',
                        'data': {
                            'err_code': 0,
                            'friend_id': friend_id
                        }
                    }
                    try:
                        InfoHandler.clients[friend_id].write_message(send_message)
                    except Exception as e:
                        print("Exception: {0}".format(e))
                        self.add_friend_request(friend_id, user)
                else:
                    self.add_friend_request(friend_id, user)
                send_message_back = {
                    'type': 'add_friend_wait',
                    'data': {
                        'err_code': 0,
                        'message': "Add friend request send, please wait",
                        'result': True
                    }
                }
                try:
                    self.write_message(send_message_back)
                except Exception as e:
                    print("Exception: {0}".format(e))
        else:
            send_message = {
                'type': 'add_friend_failed',
                'data': {
                    'err_code': 0,
                    'result': False,
                    'message': result['message']
                }
            }
            try:
                self.write_message(send_message)
            except Exception as e:
                print("Exception: {0}".format(e))
            return

    async def handle_add_friend_submit(self, friend_id):
        add_result = await self.add_friend(user, friend_id)
        if add_result['err_code'] != 0:
            self.write_message(error_send_message)
            return

        if add_result['result']:
            send_message = {
                'type': 'add_friend',
                'data': {
                    'err_code': 0,
                    'result': True,
                    'message': "Add friend success"
                }
            }
        else:
            send_message = {
                'type': 'add_friend',
                'data': {
                    'error_code': 1,
                    'result': False,
                    'message': "Add friend failed"
                }
            }
        self.write_message(send_message)
        return

    async def handle_delete_friend(self, friend_id):
        error_send_message = {
            'type': 'delete_friend',
            'data': {
                'err_code': 1,
                'message': 'Server error'
            }
        }
        user = self.get_current_user()
        if user is None:
            self.close()
            return
        exist = await self.check_id_in_friend_list(user, friend_id)
        if exist['err_code'] != 0:
            self.write_message(error_send_message)
            return
        if exist['result']:
            delete_result = await self.delete_friend(user, friend_id)
            if delete_result['err_code'] != 0:
                self.write_message(error_send_message)
                return
            if delete_result['result']:
                send_message = {
                    'type': "delete_friend",
                    'data': {
                        'err_code': 0,
                        'result': True,
                        'message': "Delete friend success"
                    }
                }
                self.write_message(send_message)
                return
            else:
                send_message = {
                    'type': "delete_friend",
                    'data': {
                        'err_code': 1,
                        'result': False,
                        'message': "Delete friend failed"
                    }
                }
                self.write_message(send_message)
                return
        else:
            send_message = {
                'type': "delete_friend",
                'data': {
                    'err_code': 0,
                    'result': True,
                    'message': "Not in friend list"
                }
            }
            self.write_message(send_message)
            return

    async def echo(self, info):
        message = {
            'type': 'echo',
            'data': info
        }
        self.write_message(message)

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
            data = await db.User.find_one({'_id': username}, projection={'_id': 0, 'friendlist': 1, 'unread': 1})
            result['data']['friend_list'] = sorted(data.get('friendlist', []))
            unread = data.get('unread', None)
            if unread is not None:
                result['data']['friend_request'] = unread.get('friend_request', [])
                result['data']['unread_message_number'] = unread.get('unread_message_number', {})
            self.write_message(result)
        except Exception as e:
            print("Exception: {0}".format(e))
            del result['data']
            result['success'] = False
            result['message'] = "Server Error"
            self.write_message(result)

        return

    async def on_message(self, message):
        handler = {
            'get_all': self.handle_get_all,
            'add_friend_request': self.handle_add_friend_request,
            'delete_friend': self.handle_delete_friend,
            'echo': self.echo,
            'close': self.close_connect
        }
        try:
            message_dict = json.loads(message)
            await handler[message_dict['type']](message_dict['data'])
        except Exception as e:
            print("Exception {0}".format(e))
        return
