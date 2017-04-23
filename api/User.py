from tornado.web import authenticated
from handler.base import BaseHandler
from handler.InfoHandler import InfoHandler
from tornado.escape import json_decode


class UserHandler(BaseHandler):
    @authenticated
    async def get(self):
        pass

    @authenticated
    async def handle_friend_request(self, username, friend_id):
        result_success = {
            'success': True
        }
        result_fail = {
            'success': False
        }
        if username == friend_id:
            result_fail['message'] = "Can't add yourself as friend"
            return result_fail

        result = await self.check_user_exists(friend_id)
        if not result['success']:
            return result

        result = await self.check_id_not_in_friend_list(username, friend_id)
        if not result['success']:
            return result

        result = await self.check_id_not_in_friend_request_list(friend_id, username)
        if not result['success']:
            return result

        result = await self.add_friend_request(username, friend_id)
        if not result['success']:
            return result

        if friend_id in InfoHandler.clients:
            destination = InfoHandler.clients[friend_id]
            message = {
                'type': "add_friend_request",
                'data': username
            }
            try:
                destination.write_message(message)
            except Exception as e:
                print("Exception: {0}".format(e))

        return result_success

    @authenticated
    async def handle_friend_accept(self, username, friend_id):
        result = await self.accept_add_friend(username, friend_id)
        if result['success']:
            if friend_id in InfoHandler.clients:
                destination = InfoHandler.clients[friend_id]
                message = {
                    'type': "accept_friend_request",
                    'data': username
                }
                try:
                    destination.write_message(message)
                except Exception as e:
                    print("Exception: {0}".format(e))

        return result




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

        handler = {
            'request': self.handle_friend_request,
            'accept': self.handle_friend_accept,
            'reject': self.handle_friend_reject
        }
        request_type = data.get('type', None)
        friend_id = data.get('id', None)
        if request_type not in handler or friend_id is None:
            result_fail['message'] = "Request format error"
            self.write(result_fail)
            self.flush()
            return

        result = await handler.get(request_type)(username, friend_id)
        self.write(result)
        self.flush()
        return

    @authenticated
    async def delete(self):
        pass
