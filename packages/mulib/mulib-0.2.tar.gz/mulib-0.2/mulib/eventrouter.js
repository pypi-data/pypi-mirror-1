/**
 * @file eventrouter.js
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

var _target_id = '';
var transforms = {
  '__initialize__': function(data) {
    try {
      var foo = event_initialize;
    } catch (e) {
      return;
    }
    event_initialize(data);
  }
}

var _get_dirty_events = function(request_id) {
  var req = new XMLHttpRequest();
  var ready_state_func = function() {
//    console.log("Request status " + req.status);
    if (this.req.readyState == 4) {
      if (typeof(console) != 'undefined') {
        console.log(this.req.responseText);
      }
      if (!this.req.responseText) return; // empty response from server, we're done

      var result = evalJSON(this.req.responseText);
      var events = result.events;
      _target_id = result.target_id;
      if (events != null) {
        for (var i = 0; i < result.events.length; i++) {
      var transformer = transforms[result.events[i][0]]
      if (!transformer) {
        console.warn(result.events[i][0] + ' is not the name of a transformer.')
      } else {
          transformer(evalJSON(result.events[i][1]));
      }
        }
      }
      _get_dirty_events(result.request_id);
    } else {
//        console.log("Request readystate: " + req.readyState);
    }
  };
  ready_state_func.req = req;
  req.onreadystatechange = ready_state_func;

  req.open('POST', document.location + 'events?request_id=' + request_id, true);
  req.send(' ');
}

window.onload = function() {
  _get_dirty_events('');
}

var _send_data_is_busy = 0;
var _send_data_queue = [];

var _actually_send_data = function() {
  var req = new XMLHttpRequest();
  var ready_state_func = function() {
    if (req.readyState == 4) {
      if (_send_data_queue.length) {
        _actually_send_data();
      } else {
        _send_data_is_busy = 0;
      }
    }
  };
  ready_state_func.req = req;
  req.onreadystatechange = ready_state_func;
  var data = _send_data_queue.shift()
  _send_data_is_busy = 1;
  var the_location = document.location.toString();
  if (the_location.substr(the_location.length - 1, 1) == '/') {
    the_location = the_location.substr(0, the_location.length - 1)
  }
  req.open(
    'POST',
    the_location + '?post=' + data[0] +
    '&target_id=' + _target_id,
    true);
  req.setRequestHeader('content-type', 'application/json');
  req.send(serializeJSON(data[1]));
}

var send_data = function(event_name, data) {
  _send_data_queue.push([event_name, data]);
  if (!_send_data_is_busy) {
    _actually_send_data();
  }
}

var scroll_to_bottom = function() {
    var bottom = document.getElementById('bottom')
    if (bottom.scrollIntoView) {
        bottom.scrollIntoView()
    } else {
        window.scrollTo(0, 9999999);
    }
}

var show_hide = function(shown, id, show_node, hide_node, content) {
    var shower_style = shown ? 'display: none' : 'display: inline'
    var hider_style = shown ? 'display: inline' : 'display: none'
    var body_style = shown ? 'display: block': 'display: none'
    return [
        SPAN({
            'id': 'show-node-' + id,
            'class': 'show-node',
            'style': shower_style,
            'onclick': function() {
                $('show-node-' + id).style.display = 'none'
                $('hide-node-' + id).style.display = 'inline'
                $('body-node-' + id).style.display = 'block'
        }}, show_node),
        SPAN({
            'id': 'hide-node-' + id,
            'class': 'hide-node',
            'style': hider_style,
            'onclick': function() {
                $('show-node-' + id).style.display = 'inline'
                $('hide-node-' + id).style.display = 'none'
                $('body-node-' + id).style.display = 'none'
        }}, hide_node),
        DIV({'id': 'body-node-' + id, 'class': 'body-node', 'style': body_style}, content)]
}

var inline_iframe = function(value, dont_resize) {
    return createDOM('iframe', {
        'src': 'data:text/html,' + encodeURI(value),
        'style': 'width: 90%; border: none; height: 90%',
        'onload': function() {
            if (!dont_resize) {
                innerDoc = (this.contentDocument) ? this.contentDocument : this.contentWindow.document;
                objToResize = (this.style) ? this.style : this;
                objToResize.height = innerDoc.body.scrollHeight + 20 + 'px';
                objToResize.width = innerDoc.body.scrollWidth + 5 + 'px';
            }
        }
    })
}

