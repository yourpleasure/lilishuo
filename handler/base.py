from tornado.web import RequestHandler
from tornado.web import authenticated


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user is None:
            return None
        return user.decode()

    @authenticated
    async def check_user_exists(self, username):
        db = self.application.db
        result_success = {
            'success': True
        }
        result_fail = {
            'success': False
        }
        try:
            count = await db.User.find({'_id': username}, projection={'_id': 1}).count()
            if count > 0:
                return result_success
            result_fail['message'] = "User not exists"
            return result_fail
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def check_id_not_in_friend_list(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            exist = await db.User.find_one({'_id': username, 'friend_list': {'$elemMatch': {"$eq": friend_id}}},
                                           projection={'_id': 1})
            if exist is None:
                return result_success
            else:
                result_fail['message'] = "Already in friend_list"
                return result_fail
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server Error"
            return result_fail

    @authenticated
    async def add_friend_request(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            exist = await db.User.find_one_and_update(
                {'_id': friend_id},
                {'$addToSet': {'unread.friend_request': username}},
                projection={'_id': 1}
            )
            if exist is not None:
                return result_success
            else:
                result_fail['message'] = "Add friend failed"
                return result_fail
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server Error"
            return result_fail

    @authenticated
    async def check_id_not_in_friend_request_list(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            exist = await db.User.find_one({
                '_id': username,
                'unread.friend_request': {'$elemMatch': {"$eq": friend_id}}
            })
            if exist is None:
                return result_success
            else:
                result_fail['message'] = "Already in request list"
                return result_fail
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server Error"
            return result_fail

    @authenticated
    async def check_id_in_friend_list(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            exist = await db.User.find_one({
                '_id': username,
                'unread.friend_request': {'$elemMatch': {"$eq": friend_id}}
            })
            if exist is not None:
                return result_success
            else:
                result_fail['message'] = "Already in request list"
                return result_fail
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server Error"
            return result_fail

    @authenticated
    async def accept_add_friend(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            result1 = await db.User.find_one_and_update(
                {'_id': username},
                {"$addToSet": {'friend_list': friend_id}, "$pull": {"unread.friend_request": friend_id}},
                projection={'_id': 1}
            )
            result2 = await db.User.find_one_and_update(
                {'_id': friend_id},
                {"$addToSet": {'friend_list': username}},
                projection={'_id': 1}
            )
            if result1 is None or result2 is None:
                result_fail['message'] = "Accept friend request failed"
                return result_fail
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def reject_add_friend(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            result1 = await db.User.find_one_and_update(
                {'_id': username},
                {"$pull": {"unread.friend_request": friend_id}},
                projection={'_id': 1}
            )
            result2 = await db.User.find_one_and_update(
                {'_id': friend_id},
                {"$addToSet": {"unread.friend_rejection": username}},
                projection={'_id': 1}
            )
            if result1 is None or result2 is None:
                result_fail['message'] = "Reject friend request failed"
                return result_fail
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def delete_friend(self, username, friend_id):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            result1 = await db.User.find_one_and_update(
                {'_id': username},
                {"$pull": {"friend_list": friend_id}},
                projection={'_id': 1}
            )
            result2 = await db.User.find_one_and_update(
                {'_id': friend_id},
                {"$pull": {"friend_list": username}},
                projection={'_id': 1}
            )
            if result1 is None or result2 is None:
                result_fail['message'] = "Delete friend failed"
                return result_fail
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail

    @authenticated
    async def clear_reject(self, username, clear_list):
        db = self.application.db
        result_success = {
            "success": True
        }
        result_fail = {
            "success": False
        }
        try:
            result = await db.User.find_one_and_update(
                {'_id': username},
                {"$pullAll": {"unread.friend_rejection": clear_list}},
                projection={'_id': 1}
            )
            if result is None:
                result_fail['message'] = "Delete reject info failed"
                return result_fail
            return result_success
        except Exception as e:
            print("Exception: {0}".format(e))
            result_fail['message'] = "Server error"
            return result_fail
