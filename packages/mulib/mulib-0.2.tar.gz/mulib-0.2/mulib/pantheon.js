/**
 * @file pantheon.js
 * @author Donovan Preston
 *
 * Copyright (c) 2007, Linden Research, Inc.
 * $License$
 
 To implement the user interface of a Pantheon, create a javascript
 file with a main function. Use the observe function to register a
 callback which will be called any time the REST store changes. to
 send events to other clients, use MochiKit's doXHR (or your favorite
 XmlHttpRequest library) to perform PUT and DELETE operations on the
 store. All observers of that path will get the new document delivered
 to them.

    function main() {
        // implements a text box anyone can edit,
        // changes will be visible to everyone looking at the page
        replaceChildNodes(
            'contents',
            'Hello:',
            INPUT({
                'id': 'hello',
                'onchange': function() {
                    doXHR('hello', {
                        'method': 'PUT',
                        'headers': {'Content-type': 'application/json'},
                        'sendContent': serializeJSON(this.value)})
                }}));

        // implement the observer so we see other's changes
        observe('hello', function(event, path, body) {
            getElement('hello').value = body;
        });
    }
 */


if (!console) {
    var console = {'log': function() {}}
}


var epoch = new Date();
var _client_id = epoch.toLocaleString() + '(' + Math.random() + ')';
var _callbacks = {};
var _etags = {};
var _outstanding_requests = 0;


function get_client_id() {
    return _client_id;
}


function observe(path, callback, fetch) {
//    console.log('observe', path, callback);
    _callbacks[path] = callback;
    _get_dirty_events(true);
}


function unobserve(path) {
    delete _callbacks[path];
    _get_dirty_events(true);
}


function _get_dirty_events(replace_outstanding_request) {
    if (!replace_outstanding_request && _outstanding_requests) {
        return;
    }

    _outstanding_requests++;

    var watching = [];
    for (var path in _callbacks) {
        var etag = _etags[path];
        var rec = {'path': path};
        if (etag) {
            rec['etag'] = etag;
        }
        watching.push(rec);
    }
//    console.log(watching)

    doXHR(document.location.toString(), {
        'method': 'POST',
        'headers': {
            'Accept': 'application/json',
            'Content-Type': 'application/json'},
        'sendContent': serializeJSON({
            'client-id': _client_id,
            'observe': watching})}
    ).addCallback(
        function(req) {
            _outstanding_requests--;

            //console.log("Request status " + req.status);
            //console.log(req.responseText);
            if (!req.responseText) {
                //console.log("Empty response from server; stopping");
                return; // empty response from server, we're done
            }
            
            var result = evalJSON(req.responseText);
            //console.log(
            //    "notify: " + result.to_notify + "; " + result.path + "; "
            //    + result.event + "; " + result.body);
            var etag = result.etag;
            _etags[result.to_notify] = etag;
            var cb = _callbacks[result.to_notify];
            if (cb) {
//                console.log(cb)
                try {
                    cb(result.event, result.path, result.body);
                } catch (exc) {
                    console.error(exc);
                }
            }

            _get_dirty_events();
        }
    ).addErrback(
        function(err) {
            _outstanding_requests--;

            if (err.req.status == 202) {
                _get_dirty_events();
                //console.log("retry")
            } else {
                console.log("error", err, err.req.status, err.req.responseText);
            }
        }
    )
}

