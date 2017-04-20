/**
    * Created by kite on 4/19/17.
    */

function register() {
    var username = document.getElementById('username');
    var password = document.getElementById('password');
    document.getElementById("register").disabled = true;
    username.disabled = true;
    password.disabled = true;
    var data = {
        'username': username.value,
        'password': password.value
    };
    $.ajax({
        type: "POST",
        url: "/register",
        data: data,
        success: function (msg) {
            var result = msg['result'];
            var alert_window = document.getElementById("alert_window");
            if (result){
                alert_window.style.left = (window.outerWidth - $(".alert_window").width())/2 + "px";
                document.getElementById("message").innerText = "Register Success! Click OK or wait 5 seconds to go to login page!";
                alert_window.style.display = 'block';
                document.getElementById("OK").onclick = function () {
                    window.location.href="/auth/login/";
                };
                setTimeout(function () {
                    window.location.href="/auth/login/";
                }, 5000);
            }
            else{
                alert_window.style.left = (window.outerWidth - $(".alert_window").width())/2 + "px";
                document.getElementById("message").innerText = "Register Failed!" + msg['message'] + "! Pleasure click OK or wait 5 seconds to try again!";
                alert_window.style.display = 'block';
                document.getElementById("OK").onclick = function () {
                    window.location.href="/register";
                };
                setTimeout(function () {
                    window.location.href="/register";
                }, 5000);
            }
        },
        error: function (e) {
            alert("Error!" + e.message + "! Please try again!");
            window.location.href="/register";
        }
    })
}