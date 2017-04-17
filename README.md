# Simple private letter -- Liulishuo written test
This is a simple private letter system like Weixin.

## Architecture
### Client side
Client side is implemented by html and some javascript. User can register an id and password and can login with the same info later. Id can be a username or an email.  
User first create an id and use it to chat with others. The message is sent to server and server will send it to the receiver.

### Server side
Server accept register info and create id for user and transform message to receiver.