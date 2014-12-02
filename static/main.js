$(document).ready(function() {

    /********* WHEN A USER LOGS INTO THE SYSTEM **********/

    // set the current room
    var currentRoom = '';

    // connect the socket
    var socket = io.connect('http://' + document.domain + ':' + location.port + "/chat");

    // join the current user to their own personal command room
    socket.emit('join room', 
                {'username':  loggedInUser, 'room':  loggedInUser}
    );
    console.log('The ' +  loggedInUser + ' is being added to room:' +  loggedInUser);

    // tell all users to refresh their list of connected users
    socket.emit('refresh connected users');

    
    /******* THE COMMAND ROOM ***********/

    // when a user's room receives a command
    socket.on('interpret command', function(data) {
        var command = data.command,
            commandBody = data.body,
            commandOrigin = data.origin;

        // if that command is a J (for join), join them to the given room
        if(command === 'J') {
            var newRoom = commandBody;

            socket.emit('join room', 
                        {'username':  loggedInUser, 'room': newRoom}
            ); 

            $('#chat-box').removeClass('hidden');

            // establish that this new room is the room we're currently talking in
            currentRoom = newRoom
        }

        // if the user receives a UL (update list) command, refresh their list of connected users
        else if(command === 'UL') {
            $('#online-users').load('/refresh_users?user=' +  loggedInUser);
        }

    });


    /************ STARTING A NEW CHAT **************/

    // when the current user clicks on a connected user
    $(document).on('click', '.user_link', function(event) {
        var userToTalkTo = $(this).attr('id');

        // create a new room name for the two users to share
        if(userToTalkTo <  loggedInUser) {
            var newRoom = userToTalkTo +  loggedInUser;
        } 
        else {
            var newRoom =  loggedInUser + userToTalkTo;
        }

        // tell the other user's command room to join this new chat
        socket.emit('receive command', 
                    {'command': 'J', 'body':newRoom, 'room': userToTalkTo}
        );
        // tell the current user's command room to join this chat
        socket.emit('receive command', 
                    {'command': 'J', 'body':newRoom, 'room':  loggedInUser}
        );
        // open a new chat window for both users
        socket.emit('open chat', 
                    {'submitting':  loggedInUser, 'receiving': userToTalkTo, 'room': newRoom}
        );

    });

    // when a request to open a chat window has been made
    socket.on('open chat box', function(event) {
        console.log(event);
        // if a window for that chat isn't open yet, open one
        if($('#' + event.chat_room).length === 0) {
            console.log("The chatroom doesn't exist yet, add it");
            var html = event.template;
            $('#chat-section').append(html);
        }
        else {
            console.log("The chatroom already exists. Don't add it");
        }

    });


    /************** MANAGING THE CHAT *****************/

    // when the user submits a message
    $(document).on('submit', 'form', function(event) {
        event.preventDefault();
        var _this = $(this),
            chat_room = _this.parent('.chat-box').attr('id'),
            message = _this.find('input[name="message"]').val(),
            ronnie = new RegExp('AskRonnie');

        // if the chat name has "AskRonnie" in it
        if(ronnie.test(chat_room)) {
            var $log = $('.log');

            // print the message the current user sent in the chat window
            $('#' + chat_room + ' div.log').append('<p class="self-color">' +  
                loggedInUser + ': ' + message + '</p>');
            $log.scrollTop($log[0].scrollHeight);

            // send that message to the ronnie socket handler for interpretation and response
            socket.emit('talk to ronnie', 
                        {'message': message, 'room': chat_room}
            );
        }
        else {
            // send the message to the server, to be directed to the appropriate user
            socket.emit('message event', 
                        {data: message, 'room': chat_room}
            );
        }

        // clear the message field
        _this.find('input[name="message"]').val('');
    });


    // if the user closes a chat window, remove it from their DOM
    $(document).on('click', '.end-chat', function(event) {
        var _this = $(this);

        // send a message telling the other user that the chat has been exited
        socket.emit('message event', 
                    {data:  loggedInUser + ' has left the chat.', 
                        'room': _this.parent('.chat-box').attr('id')}
        );
        _this.parent('.chat-box').remove();
    });


    /* when the user receives a message from another user (via the server),
       display it in the log*/
    socket.on('message to display', function(response) {
        var chatRoom = response.room,
            $log = $('.log'),
            $chatRoomLog = $('#' + chatRoom + ' div.log');

        if(response.user ===  loggedInUser) {
            $chatRoomLog.append('<p class="self-color">' + response.user + ': ' + 
                response.message + '</p>');
        }
        else {
            $chatRoomLog.append('<p class="other-color">' + response.user + ': ' + 
                response.message + '</p>');
        }
        $log.scrollTop($log[0].scrollHeight);
        
    });

    // when the user clicks Ronnie's 'text this address' link
    $(document).on('click', '.get_phone', function(event) {
        event.preventDefault();
        num = prompt('Please enter your phone number', '(xxx)xxx-xxxx')
        var href = $(this).attr('href') + num;
        console.log(href);
        $.get(href);
    });

    // handles app messages, ex: 'x user has left the chat'
    socket.on('app message display', function(response) {
        var chatRoom = response.room,
            $log = $('.log'),
            $chatRoomLog = $('#' + chatRoom + ' div.log');

        $chatRoomLog.append('<p>' + response.message + '</p>');
        $log.scrollTop($log[0].scrollHeight);
    });


    /******************* ON LOGOUT ************************/

    // when a user logs out, tell all users to refresh their conencted list
    $(document).on('click', '#logout', function(event) {
        socket.emit('refresh connected users');         
    });


    /************** BUTTON/CHATBOX GENERAL STYLING ***************/

    $(document).on('mousedown', '.button-style', function(event) {
        $(this).css('backgroundColor', 'lightGrey');
    });

    $(document).on('mouseup', '.button-style', function(event) {
        $(this).css('backgroundColor', 'gray');
    });

    $(document).on('focusout', '.chat-box', function(event) {
        $(this).addClass('blurred');
    });

    $(document).on('focusin', '.chat-box', function(event) {
        $(this).removeClass('blurred');
    });



});