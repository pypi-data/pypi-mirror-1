
function confirmDelete(what, id) {
    return confirm("Delete "+what+" "+id+"?");
}

function showFlashStatusMessage() {
    var flashData = document.getElementById('flashTransport');
    if (flashData.value != "") {
        statusmessage = flashData.value
        if (statusmessage[0] == 'S') {
            $.flash.success('Success', '...... '+statusmessage);
        } else {
            $.flash.error('Failure', '...... '+statusmessage);
        }
    }
}

function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
        window.onload = func;
    } else {
        window.onload = function() {
            oldonload();
            func();
        }
    }
}

addLoadEvent(showFlashStatusMessage);
