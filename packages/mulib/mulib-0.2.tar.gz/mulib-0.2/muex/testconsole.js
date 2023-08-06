/**
 * @file testconsole.js
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


var counters = {
	'test_success': 0,
	'test_failure': 0,
	'test_error': 0
}

event_initialize = function(data) {
	document.title = 'backbone: ' + data
	replaceChildNodes('contents',
		DIV({'class': 'button-bar'},
			SPAN({'id': 'test-timer', 'class': 'test-counter'}),
			SPAN({'id': 'test_success', 'class': 'test_success test-counter'}, 0),
			SPAN({'id': 'test_failure', 'class': 'test_failure test-counter'}, 0),
			SPAN({'id': 'test_error', 'class': 'test_error test-counter'}, 0),
			FORM({'style': 'display: inline', 'onsubmit': function() {
				send_data('run_suite', $('test_suite_input').value)
				return false }},
				SELECT({'id': 'test_suite_input'},
					OPTION({}, 'static'),
					OPTION({}, 'sim'),
					OPTION({}, 'grid'),
					OPTION({}, 'broken')),
				BUTTON({}, "run suite")),
			FORM({'style': 'display: inline', 'onsubmit': function() {
					send_data('run', $('test_module_input').value)
					return false }},
				INPUT({'type': 'text', 'id': 'test_module_input'}),
				BUTTON({}, "run"))),
		data,
		DIV({'id': 'test-results'}))
}

transforms['log_import_error'] = function(module) {
	var module_or_suite = module[0]
	var exception = module[1]
	appendChildNodes('test-results',
		DIV({'class': 'test-row test_error'},
			"Could not import: ", exception, "(", module_or_suite, ")"))
	scroll_to_bottom()
}

transforms['log_start'] = function(args) {
	counters = {
		'test_success': 0,
		'test_failure': 0,
		'test_error': 0
	}
	$('test-timer').innerHTML = ''
	$('test_success').innerHTML = 0
	$('test_failure').innerHTML = 0
	$('test_error').innerHTML = 0
	
	replaceChildNodes('test-results', DIV({'class': 'test-start'}, args[0] + ' started at ' + args[1]))
}

var current_test_id = null
var has_log_lines = false

transforms['test_start'] = function(test_id) {
	current_test_id = test_id
	has_log_lines = false
	appendChildNodes('test-results',
		DIV({'class': 'test-row', 'id': current_test_id}, SPAN({'class': 'test-id'}, current_test_id),
			DIV({'class': 'test-details', 'id': current_test_id + '-details'})))
}

transforms['log'] = function(line) {
	var line_div = DIV({'class': 'log-line'}, line)
	if (current_test_id) {
		if (has_log_lines) {
			appendChildNodes('body-node-' + current_test_id + '-log-lines', line_div)
		} else {
			has_log_lines = true
			appendChildNodes(
				current_test_id + '-details',
				DIV({'class': 'log-shell', 'id': current_test_id + '-log-shell'},
					show_hide(false, current_test_id + '-log-lines', 'Show logs', 'Hide logs', line_div)))
		}
	} else {
		// something printed while a test was not running; just spew
		appendChildNodes('test-results', line_div)
	}
}

var annotate_node = function(what_name) {
	transforms[what_name] = function(value) {
		addElementClass(current_test_id, what_name)
		counters[what_name] = counters[what_name] + 1
		$(what_name).innerHTML = counters[what_name]
		if (what_name != 'test_success') {
			var show_log_output = $('show-node-' + current_test_id + '-log-lines')
			if (show_log_output) {
				show_log_output.onclick()
			}

			appendChildNodes(
				current_test_id + '-details',
				DIV({'class': 'traceback-shell', 'id': current_test_id + '-traceback-shell'},
					show_hide(false, current_test_id + '-traceback', 'Show traceback', 'Hide traceback',
						inline_iframe(value, true))))
		}
		current_test_id = null
		has_log_lines = false
		scroll_to_bottom()
	}
}

annotate_node('test_success')
annotate_node('test_error')
annotate_node('test_failure')

transforms['log_summary'] = function(what) {
	$('test-timer').innerHTML = what[1] + ' seconds'
	appendChildNodes('test-results', DIV({'class': 'test-summary'}, what[0] + ' tests ran in ' + what[1] + ' seconds.'))
	scroll_to_bottom()
}

