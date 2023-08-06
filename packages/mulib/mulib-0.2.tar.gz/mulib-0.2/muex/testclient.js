

function submit_input() {
    doXHR('input', {
           	 'method': 'POST',
            'headers': {'Content-type': 'application/json'},
            'sendContent': serializeJSON(this.input.value)}
        );
	return false;
}


function clear() {
	replaceChildNodes(
		'contents',
		DIV({'id': 'lines'}), FORM({'id': 'input-line', 'onsubmit': submit_input}, INPUT({'name': 'input'})));
}


function main() {
	clear();

	observe('line', clear);
	observe('line/*', function(event, path, body) {
		appendChildNodes('lines', DIV({'class': 'output-lines'}, body));
	});
}

