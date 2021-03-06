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

function handle_history_message() {
    var friend_id = current_message_friend_id;
    var message_number = document.getElementById(friend_id + "_message_number").innerText;
    if (message_number === "") {
        var friend_tab = document.getElementById(friend_id + "_tab");
        var cell = friend_tab.cells[1];
        var unread_message_number = parseInt(cell.innerText);
        message_number = (-1) * unread_message_number - 1;
        cell.innerText = 0;
        cell.classList.add('empty');
    }
    else
        message_number = parseInt(message_number);
    if (message_number === 0)
        return;
    document.getElementById(friend_id + "_message").style.pointerEvents = 'none';
    $.ajax({
        type: "GET",
        url: "/api/message/"+friend_id+"/history?index=" + message_number,
        success: function (msg) {
            if (msg['success']){
                var messages = msg['data'];
                var message_box_id = friend_id + "_message";
                var friend_message_div = document.getElementById(message_box_id);
                var scroll_top = friend_message_div.scrollTop;
                var friend_pattern = new RegExp("^\\d+_" + friend_id + "$");
                document.getElementById(friend_id + "_message_number").innerText = msg['index'];
                for (var i = messages.length - 1; i >= 0; i--){
                    var message = messages[i];
                    var p = document.createElement('p');
                    p.id = message['id'];
                    p.style.border = "solid:#00000";
                    p.innerText = friend_id + ": " + message['data'];
                    if (p.id.match(friend_pattern))
                        p.classList.add('other');
                    else {
                        p.classList.add('self');
                        var delete_message_input = document.createElement('button');
                        var t = document.createTextNode("Delete");
                        delete_message_input.addEventListener('click', delete_message);
                        delete_message_input.appendChild(t);
                        p.appendChild(document.createElement('br'));
                        p.appendChild(delete_message_input);
                    }
                    friend_message_div.insertBefore(p, friend_message_div.firstChild);
                }
                friend_message_div.scrollTop = friend_message_div.scrollHeight - scroll_top;
            }
            document.getElementById(friend_id + "_message").style.pointerEvents = 'auto';
        },
        failure: function (msg) {
            alert(msg);
            document.getElementById(friend_id + "_message").style.pointerEvents = 'auto';
        }
    });
}

function test_and_send_message() {
    var event = window.event;
    if (event.keyCode === 13){
        event.preventDefault();
        send_massage();
    }
    document.getElementById("message_area");
}

function show_message() {
    var friend_id = this.firstChild.innerText;
    var message_box_id = friend_id + "_info";
    var friend_info_div = document.getElementById(message_box_id);
    if (friend_info_div === null){
        if (current_message_friend_id !== null){
            document.getElementById(current_message_friend_id + "_info").style.display = 'none';
        }
        var div = document.createElement('div');
        div.classList.add("message_info");
        div.id = message_box_id;
        div.innerHTML = document.getElementById("Hello_info").innerHTML.replace(/Hello/g, friend_id);
        document.getElementById("message_input").style.display = 'block';
        document.getElementById("delete_friend").style.display = 'block';
        document.getElementById("message_box_list").appendChild(div);
        current_message_friend_id = friend_id;
        handle_history_message();
        var friend_message_div = document.getElementById(friend_id + "_message");
        friend_message_div.scrollTop = friend_message_div.scrollHeight;
    }
    else{
        if (current_message_friend_id !== null){
            document.getElementById(current_message_friend_id + "_info").style.display = 'none';
        }else{
            document.getElementById("message_input").style.display = 'block';
            document.getElementById("delete_friend").style.display = 'block';
        }
        current_message_friend_id = friend_id;
        document.getElementById(current_message_friend_id + "_info").style.display = 'block';
        var unread_message = parseInt(this.lastChild.innerText);
        if (unread_message !== 0)
            handle_send_message(friend_id);
    }
}

function handle_friend_list(friend_list, unread_message_numbers) {
    var friend_table = document.getElementById("friend_list");
    for (var i = 0; i < friend_list.length; i++) {
        var tr = document.createElement('tr');
        var unread_number = 0;
        if (unread_message_numbers.hasOwnProperty(friend_list[i])){
            unread_number = unread_message_numbers[friend_list[i]];
        }
        tr.id = friend_list[i] + "_tab";
        tr.addEventListener('click', show_message);
        if (unread_number === 0) {
            tr.innerHTML = "<td>" + friend_list[i] + "</td><td class='empty'>" + unread_number + "</td>";
        }
        else{
            tr.innerHTML = "<td>" + friend_list[i] + "</td><td>" + unread_number + "</td>";
        }
        friend_table.appendChild(tr);
    }
}


function accept_friend_request(item) {
    var friend_request_tab = item.parentElement.parentElement;
    var friend_request_tab_id = friend_request_tab.id;
    var friend_id = friend_request_tab_id.substr(0, friend_request_tab_id.length - 6);
    document.getElementById("main").style.pointerEvents = 'none';
    var data = {
        'type': "accept",
        'data': friend_id
    };
    $.ajax({
        type: "POST",
        url: "/api/user/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            document.getElementById("main").style.pointerEvents = 'auto';
            if (msg['success'] === false){
                alert(msg['message']);
            }
            else{
                alert("Accept friend request");
                var friend_table = document.getElementById("friend_list");
                var tr = document.createElement('tr');
                tr.id = friend_id + "_tab";
                tr.addEventListener('click', show_message);
                tr.innerHTML = "<td>" + friend_id + "</td><td class='empty'>" + 0 + "</td>";
                friend_table.insertBefore(tr, friend_table.firstChild);
                friend_request_tab.remove();
                var friend_request_table = document.getElementById("friend_request_list");
                if (friend_request_table.childElementCount > 0)
                    document.getElementById("friend_request").innerText = "Friend Request(" + friend_request_table.childElementCount + ")";
                else
                    document.getElementById("friend_request").innerText = "Friend Request";
            }
        },
        error: function (e) {
            document.getElementById("main").style.pointerEvents = 'auto';
            alert("Error " + e);
        }
    });
}

function reject_friend_request(item) {
    var friend_request_tab = item.parentElement.parentElement;
    var friend_request_tab_id = friend_request_tab.id;
    var friend_id = friend_request_tab_id.substr(0, friend_request_tab_id.length - 6);
    document.getElementById("main").style.pointerEvents = 'none';
    var data = {
        'type': "reject",
        'data': friend_id
    };
    $.ajax({
        type: "POST",
        url: "/api/user/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            document.getElementById("main").style.pointerEvents = 'auto';
            if (msg['success'] === false){
                alert(msg['message']);
            }
            else{
                alert("Reject friend request");
                friend_request_tab.remove();
                var friend_request_table = document.getElementById("friend_request_list");
                if (friend_request_table.childElementCount > 0)
                    document.getElementById("friend_request").innerText = "Friend Request(" + friend_request_table.childElementCount + ")";
                else
                    document.getElementById("friend_request").innerText = "Friend Request";
            }
        },
        error: function (e) {
            document.getElementById("main").style.pointerEvents = 'auto';
            alert("Error " + e);
        }
    });
}

function handle_friend_request_list(friend_request_list) {
    var friend_request_table = document.getElementById("friend_request_list");
    for (var i = 0; i < friend_request_list.length; i++) {
        var tr = document.createElement('tr');
        tr.id = friend_request_list[i] + "_retab";
        tr.innerHTML = "<td>" + friend_request_list[i] + "</td><td><input type='button' value='Accept' onclick='accept_friend_request(this)'></td><td><input type='button' value='Reject' onclick='reject_friend_request(this)'></td>";
        friend_request_table.appendChild(tr);
    }
    if (friend_request_table.childElementCount > 0)
        document.getElementById("friend_request").innerText = "Friend Request(" + friend_request_table.childElementCount + ")";
}

function handle_friend_rejection_list(friend_rejection_list){
    for (var i = 0; i < friend_rejection_list.length; i++){
        alert("Add friend " + friend_rejection_list[i] + " rejected");
    }
    var data = {
        'type': 'clear_reject',
        'data': friend_rejection_list
    };
    $.ajax({
        type: "POST",
        url: "/api/user/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
        }
    });
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
    var friend_add_request = document.getElementById("friend_request_list");
    var request_id = friend_id + "_retab";
    if (document.getElementById(request_id) !== null)
        return;

    var tr = document.createElement('tr');
    tr.id = request_id;
    tr.innerHTML = "<td>" + friend_id + "</td><td><input type='button' value='Accept' onclick='accept_friend_request(this)'></td><td><input type='button' value='Reject' onclick='reject_friend_request(this)'></td>";
    friend_add_request.insertBefore(tr, friend_add_request.firstChild);
    document.getElementById("friend_request").innerText = "Friend Request(" + friend_add_request.childElementCount + ")";
}

function handle_accept_friend_request(friend_id) {
    alert("Add friend " + friend_id + " success");
    var tr = document.createElement('tr');
    tr.id = friend_id + "_tab";
    tr.addEventListener('click', show_message);
    tr.innerHTML = "<td>" + friend_id + "</td><td class='empty'>" + 0 + "</td>";
    var friend_list = document.getElementById("friend_list");
    friend_list.insertBefore(tr, friend_list.firstChild);
}

function handle_reject_friend_request(friend_id) {
    alert("Add friend " + friend_id + " rejected");
    var data = {
        'type': 'clear_reject',
        'data': [friend_id]
    };
    $.ajax({
        type: "POST",
        url: "/api/user/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
        }
    });
}

function handle_delete_friend(friend_id) {
    document.getElementById(friend_id + "_tab").remove();
}

function handle_send_message(friend_id) {
    var friend_tab = document.getElementById(friend_id + "_tab");
    var cell = friend_tab.cells[1];
    if (friend_id !== current_message_friend_id){
        cell.innerText = parseInt(cell.innerText) + 1;
        cell.classList.remove('empty');
    }
    else {
        cell.innerText = 0;
        cell.classList.add('empty');
        $.ajax({
            type: "GET",
            url: "/api/message/" + friend_id + "/",
            success: function (msg) {
                if (msg['success']){
                    var messages = msg['data'];
                    var message_box_id = friend_id + "_message";
                    var friend_message_div = document.getElementById(message_box_id);
                    for (var i = 0; i < messages.length; i++){
                        var message = messages[i];
                        var p = document.createElement('p');
                        p.id = message['id'];
                        p.classList.add('other');
                        p.innerText = friend_id + ": " + message['data'];
                        friend_message_div.appendChild(p);
                    }
                    friend_message_div.scrollTop = friend_message_div.scrollHeight;
                }
            },
            error: function (e) {
                alert("Error " + e);
            }
        });
    }
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
            case "reject_friend_request":
                handle_reject_friend_request(data.data);
                break;
            case "delete_friend":
                handle_delete_friend(data.data);
                break;
            case "send_message":
                handle_send_message(data.data);
                break;
        }
    }
}

function test_and_add_friend() {
    var event = window.event;
    if (event.keyCode === 13){
        event.preventDefault();
        add_friend();
    }
}

function add_friend() {
    var friend_id = document.getElementById("add_friend").value;
    document.getElementById("main").style.pointerEvents = 'none';
    var data = {
        'type': 'request',
        'data': friend_id
    };
    $.ajax({
        type: "POST",
        url: "/api/user/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
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

function delete_friend() {
    var friend_id = current_message_friend_id;
    document.getElementById("message_input").style.display = 'none';
    document.getElementById("delete_friend").style.display = 'none';
    document.getElementById(friend_id + "_tab").remove();
    document.getElementById("main").style.pointerEvents = 'none';
    current_message_friend_id = null;
    var data = {
        'data': friend_id
    };
    $.ajax({
        type: "DELETE",
        url: "/api/user/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            document.getElementById("main").style.pointerEvents = 'auto';
            if (msg['success'] === false){
                alert(msg['message']);
            }
            else{
                document.getElementById(friend_id + "_info").remove();
                alert("Delete friend " + friend_id);
            }
        },
        error: function (e) {
            document.getElementById("main").style.pointerEvents = 'auto';
            alert("Error " + e);
        }
    });
}

function delete_message() {
    var message = this.parentElement;
    var message_id = message.id;
    $.ajax({
        type: "DELETE",
        url: "/api/message/" + current_message_friend_id + "/?message_id=" + message_id,
        success: function (msg) {
            if (msg['success']){
                message.remove();
            }
            else{
                alert(msg['message']);
            }
        },
        error: function (e) {
            alert("Error " + e);
        }
    });
}

function send_massage() {
    var message_area = document.getElementById("message_area");
    var message = message_area.value;
    if (message === ""){
        return;
    }
    message_area.value = "";
    var timestamp = Date.now();
    var data = {
        'message': message,
        'timestamp': timestamp,
        'friend_id': current_message_friend_id
    };
    $.ajax({
        type: "POST",
        url: "/api/message/",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (msg) {
            if (msg['success']){
                var message_box_id = current_message_friend_id + "_message";
                var friend_message_div = document.getElementById(message_box_id);
                var p = document.createElement('p');
                var my_id = document.getElementById('header').innerText;
                p.id = timestamp + "_" + my_id;
                p.style.border = "solid:#00000";
                p.classList.add('self');
                p.innerText = my_id + ": " + message;
                var delete_message_input = document.createElement('button');
                var t = document.createTextNode("Delete");
                delete_message_input.addEventListener('click', delete_message);
                delete_message_input.appendChild(t);
                p.appendChild(document.createElement('br'));
                p.appendChild(delete_message_input);
                friend_message_div.appendChild(p);
                friend_message_div.scrollTop = friend_message_div.scrollHeight;
            }
            else{
                alert(msg['message']);
            }
        },
        error: function (e) {
            alert("Error " + e);
        }
    });
}

function strategy2() {
    alert("Unsupported browser");
}

function message_scroll(message_box) {
    var scrollTop = message_box.scrollTop;
    if(scrollTop === 0){
        handle_history_message();
    }
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