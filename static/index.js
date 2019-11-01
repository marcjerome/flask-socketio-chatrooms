var socket = io();

//Adding eventlisteners as the website load
document.addEventListener('DOMContentLoaded', () => {

    /* creating channels
     * when channel is created, newly created channel is shown to all users
     */
    socket.on('connect', () => {
        document.querySelector('#createChannelBtn').onclick = () => {
            name = document.getElementById("channelName").value;
            if (name.length > 0) {
                socket.emit("createChannel", { data: name })
            }

        }
    });

    /* eventlistener when channels are clicked
     * addEventListener is necessary although it seems redundant,
     * if removed, this functionality would not work
     */
    document.getElementById('channels').addEventListener('click', function (event) {

        // get the channel name from the clicked channel
        const target = event.target;
        const chatroom_name = target.dataset.channelname;

        //removed all the messages on the website
        document.querySelector('#messages').innerHTML = ' ';

        //leave the current room
        socket.emit("leave_chatroom");

        //join the selected room
        socket.emit("join_chatroom", { chat_room: chatroom_name });

    });

    //eventlistener for the send button in the chatroom
    document.getElementById('send-button').onclick = () => {
        let message = document.getElementById('chat-text').value;
        socket.emit("user_send", { message: message });

    }


});
//end of adding eventListeners

//show the newly created channels to all users
socket.on('showChannel', data => {
    const button = document.createElement('button');
    button.setAttribute("class", "joinChannel");
    button.setAttribute("data-channelname", `${data.select}`);
    button.innerHTML = `${data.select}`;
    document.querySelector('#channels').appendChild(button);
});


//show the previous messages  once the user selects a channel
socket.on('showMessages', data => {
    //append the previous messages of the selected channel
    if (data.channel_messages != null) {
        for (let i = 0; i < data.channel_messages.length; i++) {
            const p = document.createElement('p');
            p.innerHTML = data.channel_messages[i].user + ': ' + data.channel_messages[i].text;
            document.querySelector('#messages').appendChild(p);
        }
    }
});

//show sent messages to the user as different users chat in the chatroom
socket.on('showSentMessages', message => {
    const p = document.createElement('p');
    p.innerHTML = message.user + ': ' + message.text;
    document.querySelector('#messages').appendChild(p)
});

//show user(s) that left the chatroom
socket.on('user_left', data => {
    const p = document.createElement('div');
    p.innerHTML = `${data.user} has left the chat`;
    document.querySelector('#messages').appendChild(p);
});

//show user(s) that joins the chatroom
socket.on('user_join', data => {
    const p = document.createElement('div');
    p.innerHTML = `${data.user} has joined the chat`;
    document.querySelector('#messages').appendChild(p);
});