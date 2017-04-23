/**
 * Created by kite on 4/20/17.
 */

var ws = null;
var current_message_friend_id = null;

function destroy_websocket(){
    if (ws === null)
        return;
    var message = {
        'type': 'close',
        'data': 'close'
    };
    ws.send(JSON.stringify(message));
}

// function handle_add_friend(message) {
//     alert(message['message']);
//     var add_friend_input = document.getElementById("add_friend");
//     if (message['result']){
//         var tr = document.createElement('tr');
//         tr.id = add_friend_input.value + "_tab";
//         tr.addEventListener('click', show_message);
//         tr.innerHTML = "<td>" + add_friend_input.value + "</td><td class='empty'>" + 0 + "</td>";
//         $("#friend_list").prepend(tr);
//     }
//     add_friend_input.disabled = false;
//     var submit_add_friend = document.getElementById("submit_add_friend");
//     submit_add_friend.disabled = false;
// }
//
// function handle_delete_friend(message) {
//     alert(message['message']);
//     var friend = current_message_friend_id;
//     current_message_friend_id = null;
//     if(message['err_code'] === 0){
//         document.getElementById(friend + "_tab").remove();
//     }
//     document.getElementById("user_info").style.pointerEvents = 'auto';
// }
//
// function show_message() {
//     var friend_id = this.firstChild.innerText;
//     var unread_message = parseInt(this.lastChild.innerText);
//     var message_box_id = friend_id + "_info";
//     var friend_message_div = document.getElementById(message_box_id);
//     if (friend_message_div === null){
//         if (current_message_friend_id !== null){
//             document.getElementById(current_message_friend_id + "_info").style.display = 'none';
//         }
//         var $div = $("<div id="+ message_box_id+">").addClass("message_info");
//         var message_box = $div.html($("#Hello_info").html().replace(/Hello/g, friend_id));
//         document.getElementById("message_input").style.display = 'block';
//         document.getElementById("delete_friend").style.display = 'block';
//         $("#message_box_list").append($div);
//         current_message_friend_id = friend_id;
//     }
//     else{
//         if (current_message_friend_id !== null){
//             document.getElementById(current_message_friend_id + "_info").style.display = 'none';
//         }
//         current_message_friend_id = friend_id;
//         document.getElementById(current_message_friend_id + "_info").style.display = 'block';
//     }
// }

function handle_friend_list(friend_list, unread_message_numbers) {
    var friend_table = document.getElementById("friend_list");
    for (var i = 0; i < friend_list.length; i++) {
        var tr = document.createElement('tr');
        var unread_number = 0;
        if (unread_message_numbers.hasOwnProperty([friend_list[i]])){
            unread_number = unread_message_numbers[friend_list[i]];
        }
        tr.id = friend_list[i] + "_tab";
        tr.addEventListener('click', show_message);
        tr.innerHTML = "<td>" + friend_list[i] + "</td><td class='empty'>" + unread_number + "</td>";
        friend_table.appendChild(tr);
    }
}


function accept_friend_request() {
    var friend_request_tab_id = this.parent().id;
    var friend_id = friend_request_tab_id.substr(0, friend_request_tab_id.length - 5);

}

function reject_friend_request() {
    //TODO
}

function handle_friend_request_list(friend_request_list) {
    var friend_request_table = document.getElementById("friend_add_request");
    for (var i = 0; i < friend_request_list.length; i++) {
        var tr = document.createElement('tr');
        tr.id = friend_request_list[i] + "_retab";
        tr.innerHTML = "<td>" + friend_request_list[i] + "</td><td><input type='button' value='Accept' onclick='accept_friend_request()'></td><td><input type='button' value='Reject' onclick='reject_friend_request()'></td>";
        friend_request_table.appendChild(tr);
    }
    friend_request_table.innerText = "Friend Request(" + friend_request_list + ")";
}

function handle_friend_rejection_list(friend_rejection_list){
    for (var i = 0; i < friend_rejection_list.length; i++){
        alert("Add friend " + friend_rejection_list[i] + " rejected");
    }
}

function handle_init(message) {
    var success = message['success'];
    if (success){
        handle_friend_list(message['friend_list'], message['unread_message_numbers']);
        handle_friend_request_list(message['friend_request']);
        handle_friend_rejection_list(message['friend_rejection']);
    }
    else{
        alert(message['message']);
    }
}

function handle_add_friend_request(friend_id) {
    var friend_add_request = document.getElementById("friend_add_request");
    var request_id = friend_id + "_retab";
    if (document.getElementById(request_id) !== null)
        return;

    var tr = document.createElement('tr');
    tr.id = request_id;
    tr.innerHTML = "<td>" + friend_id + "</td><td><input type='button' value='Accept' onclick='accept_friend_request()'></td><td><input type='button' value='Reject' onclick='reject_friend_request()'></td>";
    $("#friend_add_request").prepend(tr);
    friend_add_request.innerText = "Friend Request(" + friend_add_request.childElementCount + ")";
}

function handle_accept_friend_request(friend_id) {
    alert("Add friend " + friend_id + " success");
}

function strategy1(p) {
    if (p.isTrusted) {
        var data = JSON.parse(p.data);
        switch (data.type){
            case "add_friend_request":
                handle_add_friend_request(data.data);
                break;
            case "accept_friend_request":
                handle_accept_friend_request(data.data);
                break;
        }
    }
}
//
//
function add_friend() {
    var add_friend_input = document.getElementById("add_friend");
    var submit_add_friend = document.getElementById("submit_add_friend");
    var friend_id = document.getElementById("add_friend").value;
    document.getElementById("main").style.pointerEvents = 'none';
    var data = {
        'type': 'request',
        'id': add_friend_input.value
    };
    $.ajax({
        type: "POST",
        url: "/api/user/",
        data: data,
        success: function (msg) {
            document.getElementById("main").style.pointerEvents = 'auto';
            if (msg['success'] === false){
                alert(msg['message']);
            }
            else{
                alert("Request send, pleasure wait")
            }
        },
        error: function (e) {
            document.getElementById("main").style.pointerEvents = 'auto';
            alert("Error " + e);
        }
    });
}
//
//
//
// function delete_friend() {
//     var friend_id = current_message_friend_id;
//     document.getElementById("message_input").style.display = 'none';
//     document.getElementById("delete_friend").style.display = 'none';
//     document.getElementById(friend_id + "_info").remove();
//     document.getElementById("user_info").style.pointerEvents = 'none';
//     var message = {
//         'type': 'delete_friend',
//         'data': friend_id
//     };
//     ws.send(JSON.stringify(message));
// }
//
// function send_massage() {
//
// }

function strategy2() {
    alert("Unsupported browser");
}

window.onload = function(){
    var message_height = window.innerHeight - 166;
    $(".message_text").css('height', message_height + "px");
    $(".message_info").css('height', message_height + 50 + "px");
    var message_area = document.getElementById("message_area");
    message_area.cols = (window.innerWidth -300)/8;
    $(".send_button").css('width', window.innerWidth - message_area.offsetWidth - 300);
    document.getElementById("message_input").style.display = 'none';

    $.ajax({
        type: "GET",
        url: "/api/init/",
        success: function (msg) {
            handle_init(msg);
            if ('WebSocket' in window){
                ws = new WebSocket("ws://"+ window.location.host + "/websocket");
                ws.onmessage = function (p1) {
                    strategy1(p1);
                };
            }
            else {
                strategy2();
            }
        },
        error: function (e) {
            alert("Error " + e);
        }
    });
};

window.onbeforeunload = destroy_websocket;
window.onclose = destroy_websocket;