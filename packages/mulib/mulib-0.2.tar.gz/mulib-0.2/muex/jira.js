

function main() {
	replaceChildNodes('contents', 'hello', DIV({'id': 'filters'}));

	observe('filters/*', function(event, path, body) {
		appendChildNodes('filters', DIV({}, body.name, body.author));
	});
}

