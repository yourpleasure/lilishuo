from tornado.web import authenticated
from handler.base import BaseHandler


class InitHandler(BaseHandler):
    @authenticated
    async def get(self):
        username = self.get_current_user()
        db = self.application.db
        result = {
            'success': True
        }
        try:
            data = await db.User.find_one({'_id': username},
                                          projection={
                                              '_id': 0,
                                              'friend_list': 1,
                                              'unread.friend_request': 1,
                                              'unread.unread_message_numbers': 1,
                                              'unread.friend_rejection': 1
                                          })
            result['friend_list'] = sorted(data.get('friend_list', []))
            unread = data.get('unread', None)
            if unread is not None:
                result['friend_request'] = unread.get('friend_request', [])
                result['unread_message_numbers'] = unread.get('unread_message_numbers', {})
                result['friend_rejection'] = unread.get('friend_rejection', [])
            else:
                result['friend_request'] = []
                result['unread_message_numbers'] = {}
                result['friend_rejection'] = []
            self.write(result)
            self.flush()
        except Exception as e:
            print("Exception: {0}".format(e))
            result = {
                'success': False,
                'message': 'Server error'
            }
            return result
