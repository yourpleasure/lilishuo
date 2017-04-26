# Simple private letter -- Liulishuo written test
This is a simple private letter system like Weixin.

## Architecture
### Client side
Client side is implemented by html and some javascript. User can register an id and password and can login with the same info later. Id can be a username or an email.  
User first create an id and use it to chat with others. The message is sent to server. If browser has websocket support and the receiver is online, server will send it to the receiver immediately.

### Server side
Server accept register info and create id for user and transform message to receiver.  
The Server now use tornado framework and use mongo as backend database. Message and user info stored in same document.

## Finished task
1. User can register and login. Id can be username and one must set a password.
1. After user login, he can see her contact list and all his friends.
1. It show id and unread message count of every friend. I hide  the number when unread message count is zero.
1. One can add friend by friend id, but must be accepted by friend.
1. One can delete friend but keep the messages. When the friend is add again, the message can be shown again.
1. Click a friend will enter chat view and unread message number become zero and be hidden.
1. Can send and receive message.
1. User can delete his own message.
1. Show unread message count realtime.
1. Receive message in chat view realtime.
1. Update contact list view realtime.

## Deploy
This project can't support automatic deploy now. You should deploy in by hands. I will provide a automatic deploy method (docker) later.  
Current deploy step:
1. Run a mongodb and create a readwrite account with a proper username and password
2. Change conf/DBconf.py and make sure program can read and write your specified db
3. Make sure your python version is not lower than 3.5
4. run `pip3 install -r requirements.txt`
5. run `python3 server` and then you can use browser to view the website. The port is 8888 by default.


## Short hand
1. Use mongodb as backend database and store all information of a user in one document. This may be inefficient.
1. Don't encrypt password and message. This can be unsafe.
1. Don't use https. This can be unsafe.
1. Can't do test in browser that can't support websocket.
1. Don't test in big pressure.
1. Don't perform atomic operation when we should. Some error may occur.