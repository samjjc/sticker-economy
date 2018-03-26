$(function () {
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    var socket = new ReconnectingWebSocket(ws_path);
    var user

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
            user = data.client
            console.log("Joining room " + data.join);

            ok_msg=''
            data.messages.forEach( message => {
                ok_msg+=getMessageHTML(message)
            });

            $(".room").attr("data-room-id", data.join)

            $(".room h2").text( data.title)
            $(".messages").html(ok_msg)
            
            trade_view=''
            data.trade_requests.forEach( trade => {
                trade_view+="<div id='"+trade.pk+"' class='trade'>"+
                "<h2>Request a Trade for "+trade.requested_sticker__title+"</h2>"+
                " <img src=https://storage.googleapis.com/sticker-economy/"+trade.requested_sticker__image +" alt='Sticker image' width='200'></img>"+
                "<input class='requested_quantity' type='number' min = 0, max="+trade.requested_sticker__quantity+" value = "+trade.requested_quantity+">"+
                "<img src='https://storage.googleapis.com/sticker-economy/"+trade.given_sticker__image +"' alt='Sticker image' width='200'></img>"+
                "<input class='given_quantity' type='number' min = 0, max="+trade.requested_sticker__quantity +" value = "+trade.given_quantity+">"+
                "<button class='modify'>Modify Trade</button>"
                // if not accepted, add an accept button
                if(!(user == trade.given_sticker__owner && trade.given_completed || user != trade.given_sticker__owner &&trade.requested_completed)){
                    trade_view+="<button class='accept'>Accept</button>"
                }
                trade_view+="<button class='delete'>Decline Trade</button></div>"
            })
            $("#trades").html(trade_view)
            $(".messages").scrollTop($(".messages").prop("scrollHeight"));

            //button on click functions
            $(".modify").click( function () {
                trade_pk =  $(this).parent().attr('id')
                socket.send(JSON.stringify({
                    "command": "modify",
                    "room":   $(".room").attr("data-room-id"),
                    "trade": trade_pk,
                    "requested_quantity":$("#"+trade_pk+" .requested_quantity").val(),
                    "given_quantity":$("#"+trade_pk+" .given_quantity").val(),
                }));
            })

            $(".accept").click( function () {
                socket.send(JSON.stringify({
                    "command": "confirm",
                    "room":   $(".room").attr("data-room-id"),
                    "trade": $(this).parent().attr('id'),
                }));
            })

            $(".delete").click( function () {
                socket.send(JSON.stringify({
                    "command": "delete",
                    "room":   $(".room").attr("data-room-id"),
                    "trade": $(this).parent().attr('id'),
                }));
            })



            // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
            $("#room-" + data.leave).remove();


             //handle trades
        } else if(data.traded) {
            
            //one confirm
            if(data.user) {
                ok_msg = "<div class='contextual-message text-muted'>" + data.username + " has confirmed a trade" + "</div>";
                console.log(data.user)
                console.log(user)
                if (data.user == user){
                    $('#'+data.traded+" .accept").remove()
                }

            //trade completed
            } else {
                ok_msg = "<div class='contextual-message text-muted'>A trade has been a completed</div>";
                $('#'+data.traded).remove()
            }

        } else if(data.modified){
            $('#'+data.modified+" .requested_quantity").val(data.requested_quantity)
            $('#'+data.modified+" .given_quantity").val(data.given_quantity)

        } else if(data.delete){
            $('#'+data.delete).remove()

        } else if (data.message) {
            var msgdiv = $(".messages");
            // msg types are defined in chat/settings.py
            // Only for demo purposes is hardcoded, in production scenarios, consider call a service.
                // Message
            ok_msg = "<div class='message'>" +
                "<span class='username'>" + data.username + "</span>" +
                "<span class='body'>" + data.message + "</span>" +
                "</div>";
            ok_msg = getMessageHTML(data)
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
        socket.send(JSON.stringify({
            "command": "send",
            "room":   $(".room").attr("data-room-id"),
            "message": $(".room input").val()
        }));
        $(".room input").val("");
    });

   function getMessageHTML(message) {
        ok_msg=''
        switch(message.msg_type) {
            case 1:
                ok_msg = "<div class='message'>" +
                "<span class='username'>" + message.sender__username+"</span>" +
                "<span class='body'>" + message.message + "</span>" +
                "</div>";
                break;
            case 2:
                ok_msg = "<div class='contextual-message text-muted'>"+message.message+"</div>"
                break;
            default:
                console.log("error on message: " + message)
        }
        return ok_msg
    }
});