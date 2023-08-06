//NOTE: This is ugly. Very ugly.
var form_html = 
'<form method="post" id="vote_form">' +
'    <fieldset>' +
'    <legend>Please enter a comment</legend>' +
'    <textarea name="comment" rows="10" cols="60"></textarea><br/>' +
'    <input type="submit" />' +
'    </fieldset>' +
'</form>';

function init() {
    div = document.createElement('div')
    div.setAttribute('id', 'form_container');
    div.setStyle('display', 'none');
    div.innerHTML = form_html;
    document.body.insertBefore(div, document.body.firstChild);
    
    //document.body.innerHTML =  document.body.innerHTML + form_html;
    
    window.auth_win = new Window('approve_window', {"className": "alphacube",
                                 'height': 250, 'width': 540});
    auth_win.setContent('form_container');
}
Event.observe(window, 'load', init);

function approve(url) {
    $('vote_form').action = url;
    auth_win.showCenter(true);
}

function reject(url) {
    $('vote_form').action = url;
    auth_win.showCenter(true);
}

