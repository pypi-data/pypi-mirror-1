var poppedup = "";
function getElement(psID) { 
   if(document.all) { 
      return document.all[psID]; 
   } else { 
      return document.getElementById(psID); 
   } 
}

function formData2QueryString(docForm) {

  var submitContent = '';
  var formElem;
  var lastElemName = '';
  
  for (i = 0; i < docForm.elements.length; i++) {
    
    formElem = docForm.elements[i];
    switch (formElem.type) {
      // Text fields, hidden form elements
      case 'text':
      case 'hidden':
      case 'password':
      case 'textarea':
      case 'select-one':
        submitContent += formElem.name + '=' + escape(formElem.value) + '&'
        break;
        
      // Radio buttons
      case 'radio':
        if (formElem.checked) {
          submitContent += formElem.name + '=' + escape(formElem.value) + '&'
        }
        break;
        
      // Checkboxes
      case 'checkbox':
        if (formElem.checked) {
          // Continuing multiple, same-name checkboxes
          if (formElem.name == lastElemName) {
            // Strip of end ampersand if there is one
            if (submitContent.lastIndexOf('&') == submitContent.length-1) {
              submitContent = submitContent.substr(0, submitContent.length - 1);
            }
            // Append value as comma-delimited string
            submitContent += ',' + escape(formElem.value);
          }
          else {
            submitContent += formElem.name + '=' + escape(formElem.value);
          }
          submitContent += '&';
          lastElemName = formElem.name;
        }
        break;
        
    }
  }
  // Remove trailing separator
  submitContent = submitContent.substr(0, submitContent.length - 1);
  return submitContent;
}

function restfulFormData2QueryString(docForm) {
  var submitContent = '';
  var formElem;
  var lastElemName = '';
  
  for (i = 0; i < docForm.elements.length; i++) {
    
    formElem = docForm.elements[i];
    switch (formElem.type) {
      // Text fields, hidden form elements
      case 'text':
        submitContent += escape(formElem.value) + '.'
        break;
        
      // Radio buttons
      case 'radio':
        if (formElem.checked) {
          submitContent += escape(formElem.value) + '.'
        }
        break;        
    }
  }
  // Remove trailing separator
  submitContent = submitContent.substr(0, submitContent.length - 1);
  return submitContent;
}


function updateResults(dict) {
	$("result").innerHTML = dict["result"];
	document.forms[0].reset();
}

function popup(x) {
    document.getElementById(x).style['fill-opacity'] = 0.75;
    document.getElementById('layer0').visibility = 'hidden';
    document.getElementById('_'+x).style.visibility = 'visible';
}

function popdown(x) {
    document.getElementById(x).style['fill-opacity'] = 0.5;
    document.getElementById('_'+x).style.visibility = 'hidden';
    document.getElementById('layer0').visibility = 'visible';
}

function rollover(x) {
    document.getElementById(x).style['fill-opacity'] = 0.75;
    document.getElementById('layer0').visibility = 'hidden';
    document.getElementById('_'+x).style.visibility = 'visible';
}

function rollout(x) {
    document.getElementById(x).style['fill-opacity'] = 0.5;
    document.getElementById('_'+x).style.visibility = 'hidden';
    document.getElementById('layer0').visibility = 'visible';
}

function respond(x) {
    /* alert("I got "+ x) */
    document.location.href="/rdflab/constituency/"+x;
}


/*
* display flash message
*/
function displayStatusMessage(status, msg) {
    swapDOM("statusmessage", DIV({'id': 'statusmessage'}, DIV({'class': status}, msg)));
    callLater(3, fade, "statusmessage");
    callLater(5, swapDOM, "statusmessage", DIV({'id': 'statusmessage'}, null));
}

/*
* display flash message
*/
function displayStickyStatusMessage(status, msg, timeout) {
    var msg = swapDOM('statusmessage', DIV({'id': 'statusmessage'}, DIV({'class': status}, msg)));
    if (timeout) {
        msg.hidecb = callLater(timeout, swapDOM, msg, DIV({'id': 'statusmessage'}, null));
    }
    connect(msg, 'onclick',
        function(e) {
            var msg = e.src();
            if (msg.hidecb) {
                msg.hidecb.cancel();
                }
            disconnect(msg);
            swapDOM(msg, DIV({'id': 'statusmessage'}, null));
        }
    );
}


function flashedStatusMessage() {
/*
    var flashData = getElement('flashTransport').value;
    if (flashData != "") {
        statusmsg = eval('(' + flashData + ')');
        displayStatusMessage(statusmsg['status'], statusmsg['msg']);
    }
*/
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
addLoadEvent(onTimeLine);
