/**
 * @file logconsole.js
 * @author Donovan Preston
 *
 * Copyright (c) 2005-2006, Donovan Preston
 * Copyright (c) 2007, Linden Research, Inc.
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

event_initialize = function(data) {
	document.title = 'backbone: ' + data
	var clear_button = BUTTON({'onclick': function() {
		replaceChildNodes('log-lines', '');
	}}, 'clear')
	replaceChildNodes('contents',
		DIV({'class': 'button-bar'}, clear_button),
		data,
		DIV({'id': 'log-lines'}))
}

transforms['log'] = function(line) {
  appendChildNodes('log-lines', DIV({'class': 'log-line'}, line));
}

llsd_div = function(llsd) {
  var body = DIV({})
  body.innerHTML = llsd
  return body
}

headers_node = function(headers) {
	var items = []
	for (var key in headers) {
		items.push(createDOM('dt', {'class': 'header-key'}, key))
		items.push(createDOM('dd', {'class': 'header-value'}, headers[key]))
	}
	return DIV({'class': 'headers'}, createDOM('dl', {}, items));
}

transforms['log-request'] = function(req) {
  var headers = show_hide(
	false,
	'req-headers-' + req['request-id'],
	'Show headers',
	'Hide headers',
	headers_node(req['headers']))

  var body = show_hide(
	true,
	'req-body-' + req['request-id'],
	'Show body',
	'Hide body',
	llsd_div(req['body']))

  appendChildNodes(
	'log-lines',
	DIV({'class': 'request-line'},
	  SPAN({'class': 'request-id'}, req['request-id']),
	  SPAN({'class': 'request-method'}, req['method']),
	  SPAN({'class': 'request-url'}, req['url']),
	  SPAN({'class': 'request-path'}, req['path']),
	  DIV({'class': 'request-content'},
        DIV({'class': 'request-headers'}, headers),
	    DIV({'class': 'request-body'}, body))))

  scroll_to_bottom()
}

transforms['log-response'] = function(resp) {
  var p_success = false;
  var success = 'response-failure'
  if (resp['status'] >= 200 && resp['status'] < 300) {
    success = 'response-success'
	p_success = true
  }

  var headers = show_hide(
	false,
	'resp-headers-' + resp['request-id'],
	'Show headers',
	'Hide headers',
	headers_node(resp['headers']))


  if (p_success) {
  	var body = resp['body']
  } else {
	var body = ''
  }

  body = show_hide(
	true,
	'resp-body-' + resp['request-id'],
	'Show body',
	'Hide body',
	body)

  appendChildNodes(
	'log-lines',
	DIV({'class': 'response-line ' + success},
	  SPAN({'class': 'request-id'}, resp['request-id']),
	  SPAN({'class': 'response-status'}, resp['status']),
	  DIV({'class': 'response-content'},
		DIV({'class': 'response-headers'}, headers),
		DIV({'class': 'response-body'}, body))))

  if (!p_success) {
    swapDOM(
	  'body-node-resp-body-' + resp['request-id'],
	  createDOM('iframe', {
		'src': 'data:text/html,' + encodeURI(resp['body']),
		'style': 'width: 90%; border: none',
		'onload': function() {
		    innerDoc = (this.contentDocument) ? this.contentDocument : this.contentWindow.document;
		    objToResize = (this.style) ? this.style : this;
		    objToResize.height = innerDoc.body.scrollHeight + 20 + 'px';
		    objToResize.width = innerDoc.body.scrollWidth + 5 + 'px';
		}
    }))
  }

  scroll_to_bottom()
}

transforms['log-transform'] = function(args) {
	return // not done yet

	var transform = args[0]
	var data = args[1]

	appendChildNodes(
		'log-lines',
		DIV({'class': 'transform-line'}, 
			SPAN({'class': 'transform'}, transform),
			SPAN({'class': 'data'}, data)))

	scroll_to_bottom()
}

transforms['log-send-data'] = function(args) {
	return // not done yet

	var post = args[0]
	var target = args[1]
	var body = args[2]

	appendChildNodes(
		'log-lines',
		DIV({'class': 'send-data-line'}, 
			SPAN({'class': 'post'}, post),
			SPAN({'class': 'target'}, target),
			SPAN({'class': 'body'}, body)))

	scroll_to_bottom()
}

