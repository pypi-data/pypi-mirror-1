/*
* display flash message
*/
function getElement(psID) { 
   if(document.all) { 
      return document.all[psID]; 
   } else { 
      return document.getElementById(psID); 
   } 
}

function displayStatusMessage(status, msg) {
    swapDOM("statusmessage", DIV({'id': 'statusmessage'}, DIV({'class': status}, msg)));
    callLater(3, fade, "statusmessage");
    callLater(5, swapDOM, "statusmessage", DIV({'id': 'statusmessage'}, null));
}

function flashedStatusMessage() {
    var flashData = getElement('flashTransport').value;
    if (flashData != "") {
        statusmsg = eval('(' + flashData + ')');
        displayStatusMessage(statusmsg['status'], statusmsg['msg']);
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

addLoadEvent(flashedStatusMessage);
