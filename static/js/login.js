/**
 * Created by kite on 4/16/17.
 */
window.onload = function () {
    var search_string = window.location.search;
    var regex = new RegExp("[?&]error=([^#&]*)");
    var error = regex.exec(search_string);
    if (error !== null){
        alert(error[1].replace(/\+/g, ' '));
    }
};