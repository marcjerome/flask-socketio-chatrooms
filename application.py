import os

from flask import Flask, render_template, url_for,request,redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

#List of all chatrooms, the 'general' chatroom exist as the default chatroom
channels = ['general']
#Storage for messages of specific chatrooms. 
messages = {}


@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "POST":
        #get the username and set the 'genera' channel as the default channel of the user
        session['user'] = request.form.get('username')
        session['currentChannel'] = channels[0]
        return redirect(url_for("user"))

    return render_template("index.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    '''
        the route for the chatroom    
    '''
    username = session.get('user')
    return render_template('user.html', username=username,channels=channels)


@socketio.on("createChannel")
def receive(data):
    channel_name = data["data"]
    if channel_name not in channels:
        channels.append(channel_name)
        emit("showChannel", {'select': channel_name}, broadcast=True)

@socketio.on("join_chatroom")
def select_channel(data):
    '''
        Socket for listening for selected channels. 
        it allows the user to join its selected channel
        and it sends the present messages of the selected_channel to the user
    '''

    selected_channel = data["chat_room"]
    channel_messages = messages.get(selected_channel)
    
    #the current channel needs to be stored in a session because it will be used to know what room 
    #to broadcat the user's message once the user chats in its selected channel
    session["currentChannel"] = selected_channel
  
    join_room(selected_channel)
    emit("user_join", {'user': session.get('user')}, room=selected_channel, broadcast=True)
    emit("showMessages", {'channel_messages': channel_messages}, broadcast=False, room=request.sid)


@socketio.on("user_send")
def user_send(data):
    '''
        Socket for listening when a user sends a message.
        This stores the message to the messages dict 
        and broadcasts the message to all users connected in the room
    '''
    current_channel = session.get('currentChannel')
    new_message = {
        'text': data['message'],
        'user':session.get('user')
    }
    messages.setdefault(current_channel, []).append(new_message)

    emit("showSentMessages", new_message, room=current_channel, broadcast=True)

@socketio.on("leave_chatroom")
def leavetheRoom():
    room = session.get("currentChannel")
    if room:
        user = session.get('user')
        #Only show that the user has left the chat if there are many channels present
        if len(channels) > 1:
            emit("user_left", {'user': user}, room=room, broadcast=True, include_self=False)
        leave_room(room)


if __name__ == '__main__':
    app.secret_key = '123456'
    socketio.run(app)


