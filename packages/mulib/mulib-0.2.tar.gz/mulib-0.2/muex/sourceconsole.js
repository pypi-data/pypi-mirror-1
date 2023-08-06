/**
 * @file sourceconsole.js
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


event_initialize = function(output) {
    replaceChildNodes(
        'contents',
        DIV({'id': 'file-name'}),
        DIV({'id': 'button-bar'},
        FORM({'id': 'sourceconsole', 'onsubmit': function() {
                send_data('show_source', this.sourcefile.value)
                return false
            }},
            INPUT({'name':'sourcefile'}), BUTTON({}, "show source"))),
        DIV({'id': 'source-lines'}))
}

transforms['start_file'] = function(file_name) {
    replaceChildNodes('file-name', file_name)
    replaceChildNodes('source-lines', '')
    current_indent_level = 0
}


var current_indent_level = 0
var NBSP = '\u00a0'
var INDENT = NBSP + NBSP + NBSP + NBSP


transforms['finish_line'] = function(line_data) {
    var line = [];
    var space_before = NBSP
    var space_after = true
    for (var i = 0; i < line_data.tokens.length; i++) {
        var word = line_data.tokens[i][0]
        var type = line_data.tokens[i][1]
        if (type == 'op') {
            space_before = ''
            space_after = false
        } else if (type == 'indent') {
            current_indent_level += 1
            continue
        } else if (type == 'dedent') {
            current_indent_level -= 1
            continue
        } else {
            if (space_after == false) {
                space_after = true
            } else {
                space_before = NBSP
            }
        }
        line.push(SPAN({'class': 'python-token python-' + type}, space_before, word))
    }

    var indent = '';
    for (var j = 0; j < current_indent_level; j++) {
        indent += INDENT;
    }

    var class = 'line indent-level-' + current_indent_level
    if (line_data.uncovered) {
        class += ' uncovered'
    }

    appendChildNodes(
        'source-lines',
        DIV({'class': class},
            SPAN(
                {'class': 'line-number'},
                line_data.num), 
            DIV({'id': 'line-contents'}, indent, line)))
}

transforms['error'] = function(error_message) {
    appendChildNodes(
        'source-lines',
        DIV({'class': 'error-message'}, error_message))
}
