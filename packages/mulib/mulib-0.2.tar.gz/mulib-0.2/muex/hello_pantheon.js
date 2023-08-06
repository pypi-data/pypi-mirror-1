

function observe_document(event, path, document) {
    replaceChildNodes('document', document);
}


function change_document() {
    doXHR('document', {
        'method': 'PUT',
        'headers': {'Content-type':'application/json'},
        'sendContent': serializeJSON(this.document.value)}
    );
    return false;
}


function observe_container(event, path, value) {
    var key = path[path.length - 1];
    var old_container = getElement('container-' + key)
    if (old_container) { removeElement(old_container); }
    if (event == 'DELETE') { return; }

    appendChildNodes('container',
        DIV({'id':'container-' + key, 'class':'container-row'},
            FORM({'onsubmit':remove_container_element}, 
                INPUT({'type':'hidden', 'name':'key', 'value':key}), 
                INPUT({'type':'submit', 'value':'delete'})),
            SPAN({'class':'container-key'}, key),
            SPAN({'class':'container-value'}, value))
    );
}


function add_container_element() {
    doXHR('container/' + this.key.value, {
            'method':'PUT',
            'headers':{'Content-type':'application/json'},
            'sendContent':serializeJSON(this.value.value)}
    );
    return false;
}


function remove_container_element() {
    doXHR('container/' + this.key.value, {'method':'DELETE'});
    return false;

}


function main() {
    replaceChildNodes('contents',
        DIV({'id':'document'}), 
        FORM({'onsubmit':change_document},
            INPUT({'name':'document'}),
            INPUT({'type':'submit'})),
        DIV({'id':'container'}),
        FORM({'onsubmit':add_container_element},
            INPUT({'name':'key'}),
            INPUT({'name':'value'}),
            INPUT({'type':'submit'}))
    );

    observe('document', observe_document);
    observe('container/*', observe_container);
}

