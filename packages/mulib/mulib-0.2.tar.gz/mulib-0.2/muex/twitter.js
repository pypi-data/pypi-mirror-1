

var _nodes = [];
var _usernames = [];


function create_follower(follow, publish_usernames) {
    _usernames.push(follow);
    if (publish_usernames) {
        doXHR('following', {
            'method': 'PUT',
            'headers': {'Content-type': 'application/json'},
            'sendContent': serializeJSON(_usernames)}
        );

    }
    appendChildNodes(
        'following-list',
        DIV({
            'id': 'following-username-' + follow,
            'class': 'following-username'},
            follow));

    return function(event, path, body) {
        path = path.join('/');
        console.log('follower observer' + follow + ' ' + path + ' ' + body['text']);
        if (getElement(path)) return;
        if (path.indexOf('/') == -1) return;
        var created_at = body['created_at'];
        created_at = created_at.substring(0, created_at.indexOf('+'));
        var follow_event_body = SPAN({'class': 'follow-event-body'});
        follow_event_body.innerHTML = body['text'];
        var node = DIV({
            'id': body['id'],
            'class': 'follow-event' + ' ' + 'following-username-' + follow},
            A({'href': 'http://twitter.com/' + follow},
                IMG({'src': body['user']['profile_image_url']}),
                SPAN({'class': 'following-username'}, follow)),
            follow_event_body,
            SPAN({'class': 'created-at'}, body['created_time']));

        var found = false;
        console.log('looking');
        for (var i = 0; i < _nodes.length; i++) {
            var old_node = _nodes[i];
            var created_time = old_node['created_time'];
            console.log(
                "created_time " + created_time +
                ' ' + body['created_time']);
            // TODO I know this isn't correct. I haven't been able to figure out why.
            if (parseFloat(created_time) > parseFloat(body['created_time'])) {
                _nodes = _nodes.splice(i, 0, body);
                console.log('found ' + i + ' ' + old_node['id']);
                insertSiblingNodesBefore(
                    old_node['id'].toString(), node);
                console.log('old_node');
                found = true;
                break;
            }
        }
        if (!found) {
            console.log('not found ' + body['created_time']);
            _nodes.push(body);
            appendChildNodes('follow-stream', node);
        }
    }
}


function observe_follow_usernames(event, path, follow_usernames) {
    if (follow_usernames == undefined) {
        return;
    }
    console.log(
        'got_follow_usernames ' + follow_usernames + follow_usernames.length);
    replaceChildNodes('following-list', 'Following:');
    appendChildNodes('following-list',
        FORM({'onsubmit': function() {
            console.log('follow ' + this.follow);
            create_follower(this.follow.value, true);
            this.follow.value = '';
            return false;
        }},
        INPUT({'type': 'text', 'name': 'follow'}), INPUT({'type': 'submit'})));
    for (var i=0; i < follow_usernames.length; i++) {
        var follow = follow_usernames[i];
        console.log("OBSERVE " + follow)
        observe('users/' + follow + '/*', create_follower(follow));
    }
}


function main() {
    replaceChildNodes(
        'contents',
        DIV({'id': 'follow-stream'},
            "Follow stream"),
        DIV({'id': 'following-list'}, "Following"));

    observe('following', observe_follow_usernames, true);
}

