function check_username_availability(){
      var username = getElement('username');
      var loader = getElement('loader');
      if (username.value) { 
        loader.innerHTML = '<img src="/assets/loading.gif" alt="*" /> Checking username...'; 
        var d = loadJSONDoc("/account/check_username_availability/"+username.value);
        var success = function (meta) {
            loader.innerHTML = meta;
        };
        var failure = function (err) {
            loader.innerHTML = "";
        };
        d.addCallbacks(success, failure);
    }    
}

function hide(id) {
    obj = document.getElement(id);
    obj.style.display = "none";
}

window.onload = function() {
    var myinterval = window.setInterval('test_copy_username()',300); // check msg every x seconds
}

function copy_username() {
    if(document.forms['signup'].elements['username'].value){
        document.getElementById('usernamecheck').innerHTML = document.forms['signup'].elements['username'].value;
    } else {
        document.getElementById('usernamecheck').innerHTML = '&lt;username&gt;';
        document.getElementById('loader').innerHTML = ''
    }
}

function test_copy_username() {
    if(document.forms['signup'].elements['username'].value){
        copy_username();
    }
}

function check_password() {
    p1 = document.forms['signup'].elements['password'].value;
    p2 = document.forms['signup'].elements['cpassword'].value;

    if(p1 == p2) {
        if(p1.length < 5 || p1.length > 20){
            document.getElementById('checkpassword').innerHTML = '<span class="bad">Your password must contain between 5-20 characters.</span>';
        } else {
            document.getElementById('checkpassword').innerHTML = '<span class="good">Great! Passwords match, please go on.</span>';
        }
    }
    else {
        document.getElementById('checkpassword').innerHTML = '<span class="bad">Sorry, your passwords don\'t match. Please try again.</span>';
    }
}
