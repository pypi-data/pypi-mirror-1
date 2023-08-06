/**
 * @file shellconsole.js
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

var my_name = null


event_initialize = function(args) {
    my_name = args[0]
    var welcome_message = args[1]
    replaceChildNodes(
        'contents',
        welcome_message,
        DIV({'id': 'output'}),
        FORM({'style': 'display: inline', 'onsubmit': function() {
                send_data('console_input', {'input': $('shell_input').value, 'my_name': my_name})
                $('shell_input').value = ''
                scroll_to_bottom()
                return false }},
            INPUT({'type': 'text', 'id': 'shell_input', 'onkeypress': function() {
                setTimeout(function() {
                    send_data('key_typed', {'my_name': my_name, 'current_input': $('shell_input').value})
                }, 0)
            }}),
            BUTTON({}, "execute")))
    $('shell_input').focus()
}

transforms['key-typed'] = function(data) {
    var their_name = data[0]
    var their_line = data[1]
    var typing_node = $(their_name + '-currently-typing')
    if (their_line) {
        if (!typing_node) {
            typing_node = DIV({'id': their_name + '-currently-typing', 'class': 'log-line typing-line'},
                SPAN({'class': 'line-owner'}, their_name),
                SPAN({'id': their_name + '-current-text'}))
            appendChildNodes('output', typing_node)
        }
        $(their_name + '-current-text').innerHTML = their_line
    } else {
        if (typing_node) {
            removeElement(their_name + '-currently-typing')
        }
    }
}

transforms['output-line'] = function(line) {
	appendChildNodes('output', DIV({'class': 'log-line'}, line))
}

transforms['input-line'] = function(data) {
    var their_name = data[0]
    var prompt = data[1]
    var line = data[2]
    if (their_name != my_name && $(their_name + '-currently-typing')) {
        removeElement(their_name + '-currently-typing')
    }
	appendChildNodes(
	   'output',
	   DIV({'class': 'log-line input-line'},
	       SPAN({'class': 'line-owner'}, my_name),
	       SPAN({'class': 'prompt'}, prompt),
	       line))
}
