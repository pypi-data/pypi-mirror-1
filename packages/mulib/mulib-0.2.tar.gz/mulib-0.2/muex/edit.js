
// cookie utilities

function set_cookie(name, value) {
	document.cookie = name + "=" + value + "; path=/";
}

function get_cookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

// edit.js

var max_line_no = 0;
var changed = {};
var my_user_info;

function onfocus_line() {
  var lineno = this.id.slice(5);
  doXHR('line/' + lineno, {
		'method': 'PUT',
	    'headers': {'Content-type': 'application/json'},
		'sendContent': serializeJSON({'line':this.value, 'selected-by-color':my_user_info['color']})});
  return false;
}

function onchange_line() {
  var lineno = this.id.slice(5);
  changed[lineno] = true;
  doXHR('line/' + lineno, {
	'method': 'PUT',
	  'headers': {'Content-type': 'application/json'},
	  'sendContent': serializeJSON({'line':this.value, 'last-edited-by-color': my_user_info['color']})});
  return false;
}

function onblur_line() {
  var lineno = this.id.slice(5);
  var value = this.value;
  var color = this.style.backgroundColor;

  // defer the following code until after onchange has fired (or not)
  setTimeout(function() {
    if (changed[lineno]) {
      delete changed[lineno];
      return;
    }
    doXHR('line/' + lineno, {
	'method': 'PUT',
	  'headers': {'Content-type': 'application/json'},
	  'sendContent': serializeJSON({'line':value, 'last-edited-by-color':color})});
  }, 0);
  return false;
}


function observe_line(event, path, line_info) {
  var line_no = parseInt(path[path.length - 1]);
  if(line_no > max_line_no) {
	max_line_no = line_no;
  }
  var line_id = "line_" + line_no;
  var line_dom = $(line_id);

  if(line_dom) {
	line_dom.value = line_info['line'];
	line_dom.style.backgroundColor = line_info['last-edited-by-color'];
  } else {
	line_dom = INPUT({'class':'editable-line', 'id':line_id, 
						'value': line_info['line'],
						 'onfocus': onfocus_line, 'onblur': onblur_line, 'onchange': onchange_line});
	
	var found = false;
	for (var i = line_no - 1; i >= 0; i--) {
	  var candidate_sibling = $("line_" + i);
	  if (candidate_sibling) {
		insertSiblingNodesAfter(candidate_sibling, line_dom);
		found = true;
		break;
	  }
	}
	if (!found) {
	  replaceChildNodes('file-contents', line_dom);
	}
  }
  // console.log('yay');

  if(line_info['selected-by-color']) {
	line_dom.style.border = '1px solid ' + line_info['selected-by-color'];
  } else if(line_info['last-edited-by-color']) {
	line_dom.style.backgroundColor = line_info['last-edited-by-color'];
  } else {
	line_dom.style.border = 'none';
	line_dom.style.backgroundColor = 'none';
  }
  
  // console.log('boo');
};

function onchange_newline() {
  new_line_no = max_line_no + 1;
  doXHR('line/' + new_line_no.toString(), {
	'method': 'PUT',
	  'headers': {'Content-type': 'application/json'},
	  'sendContent': serializeJSON({'line':this.value})});
  this.value = '';
  return false;
};

function login_form() {
  doXHR('login', {
	'method': 'POST',
	  'headers': {'Content-type': 'application/json', 'Accept': 'application/json'},
	  'sendContent': serializeJSON({
		'username': this.username.value,
		'color': this.color.value,
		'picture': this.picture.value})}
  ).addCallback(function(xhr) {
  		my_user_info = evalJSON(xhr.responseText);
		set_cookie('user_info', serializeJSON(my_user_info));
  		logged_in(my_user_info);
  	}
  ).addErrback(function(err) {// console.log("login error: " + err);
    });
  return false;
}

function main() {
	my_user_info = get_cookie('user_info');
	if (my_user_info) {
		my_user_info = evalJSON(my_user_info);
		logged_in(my_user_info);
	} else {
	  replaceChildNodes('contents',
						FORM({'onsubmit': login_form},
							 LABEL({'for': 'username'}, 'Username:'),
							 INPUT({'type': 'text', 'name': 'username'}),
							 LABEL({'for': 'color'}, 'Color (eg yellow, blue):'),
							 INPUT({'type': 'text', 'name': 'color'}),
							 LABEL({'for': 'username'}, 'Picture url:'),
							 INPUT({'type': 'text', 'name': 'picture'}),
							 INPUT({'type': 'submit'})));
	}
}

function observe_user(event, path, user) {
  // console.log("user is " + path + ' ' + user);
  appendChildNodes('userlist', DIV({'style': 'background-color: ' + user['color']}, user['username']));
}

function logged_in(my_user_info) {
  replaceChildNodes(
    'contents',
	DIV({'id': 'file-contents'}),
	DIV({'id': 'userlist'}),
	INPUT({'class':'editable-line', 'id':'newline', 'onchange': onchange_newline})
	);
  observe("line/*", observe_line, true);
  observe("user/*", observe_user, true);
}

