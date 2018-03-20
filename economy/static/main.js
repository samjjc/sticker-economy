$(function () {
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    var socket = new ReconnectingWebSocket(ws_path);

    // Helpful debugging
    socket.onopen = function () {
        console.log("Connected to chat socket");
        $("li.room-link").removeClass("joined");
        roomId = $("li.room-link").attr("data-room-id");
        // Join room
        $("li.room-link").first().addClass("joined");
        socket.send(JSON.stringify({
            "command": "join",
            "room": roomId
        }));
    };
    socket.onclose = function () {
        console.log("Disconnected from chat socket");
    };

    socket.onmessage = function (message) {
        // Decode the JSON
        console.log("Got websocket message " + message.data);
        var data = JSON.parse(message.data);
        // Handle errors
        if (data.error) {
            alert(data.error);
            return;
        }
        // Handle joining
        if (data.join) {
            console.log("Joining room " + data.join);

            ok_msg=''
            data.messages.forEach( message => {
                ok_msg += "<div class='message'>" +
                "<span class='username'>" + message.sender__username + "</span>" +
                "<span class='body'>" + message.message + "</span>" +
                "</div>";
            });

            // var roomdiv = $(
            //     "<div class='room' id='room-" + data.join + "'>" +
            //     "<h2>" + data.title + "</h2>" +
            //     "<div class='messages'> "+ok_msg+"</div>" +
            //     "<input><button>Send</button>" +
            //     "</div>"
            // );
            $(".room").attr("data-room-id", data.join)

            $(".room h2").text( data.title)
            $(".messages").html(ok_msg)

            // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
            $("#room-" + data.leave).remove();
        } else if (data.message || data.msg_type != 0) {
            var msgdiv = $(".messages");
            // msg types are defined in chat/settings.py
            // Only for demo purposes is hardcoded, in production scenarios, consider call a service.
                // Message
            ok_msg = "<div class='message'>" +
                "<span class='username'>" + data.username + "</span>" +
                "<span class='body'>" + data.message + "</span>" +
                "</div>";
            msgdiv.append(ok_msg);
            msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
        } else {
            console.log("Cannot handle message!");
        }
    };

    // Says if we joined a room or not by if there's a div for it
    function inRoom(roomId) {
        return $("#room-" + roomId).length > 0;
    };

    // Room join/leave
    $("li.room-link").click(function () {
        $("li.room-link").removeClass("joined");
        roomId = $(this).attr("data-room-id");
        // Join room
        $(this).addClass("joined");
        socket.send(JSON.stringify({
            "command": "join",
            "room": roomId
        }));
    });

    $(".room button").click( function () {
        console.log("CLICKES")
        socket.send(JSON.stringify({
            "command": "send",
            "room":   $(".room").attr("data-room-id"),
            "message": $(".room input").val()
        }));
        $(".room input").val("");
    });
});