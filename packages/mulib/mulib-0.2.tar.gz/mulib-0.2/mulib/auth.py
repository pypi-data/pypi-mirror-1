"""\
@file auth.py
@author Donovan Preston

Copyright (c) 2005-2006, Donovan Preston
Copyright (c) 2007, Linden Research, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import md5
import sets
import time


from mulib import mu


REQUIRED_PARAMS = sets.Set(
    ["username", "realm", "nonce", "uri", "response", "qop", "nc", "cnonce"])


class Challenge(mu.Resource):
    def __init__(self, realm):
        self.realm = realm

    def handle(self, req):
        req.response(401)
        req.set_header(
            'WWW-Authenticate',
            'Digest realm="%s", nonce="%s", '
            'digest-uri="%s", '
            'algorithm="MD5", qop="auth"' % (
                self.realm,
                md5.md5(
                    "%d:%s" % (
                        time.time(), self.realm)).hexdigest(),
                req.uri()))

        req.write('')


class Unauthorized(mu.Resource):
    def handle(self, req):
        req.response(400)
        req.write('Unauthorized')


class DigestAuth(mu.Resource):
    def __init__(self, delegate, realm, users):
        self.delegate = delegate
        self.realm = realm
        self.users = users

    def _get_response_resource(self, req):
        auth = req.get_header('authorization', '')
        if not auth.strip():
            return Challenge(self.realm)

        auth_scheme, auth_params = auth.split(' ', 1)
        if auth_scheme.lower() != 'digest':
            return Unauthorized()

        param_map = dict()
        for key, value in [x.split('=', 1) for x in auth_params.split(', ')]:
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            param_map[key.strip()] = value

        if not REQUIRED_PARAMS.issubset(sets.Set(param_map.keys())):
            return Unauthorized()

        req.username = param_map['username']

        secret = md5.md5(
            "%s:%s:%s" % (
                req.username,
                self.realm,
                self.users.get(req.username, ''))).hexdigest()

        a2 = md5.md5("%s:%s" % (req.method(), req.uri())).hexdigest()
        param_map['a2'] = a2

        response = md5.md5(
            "%s:%s" % (
                 secret,
                "%(nonce)s:%(nc)s:%(cnonce)s:%(qop)s:%(a2)s" % param_map)
        ).hexdigest()

        if param_map['response'] != response:
            return Challenge(self.realm)
        ## Whew, we're authorized
        return self.delegate

    def findChild(self, req, segments):
        delegate = self._get_response_resource(req)
        if delegate != self.delegate:
            ## Either a challenge or unauthorized;
            ## Consume all segments
            return (delegate, segments, ())
        ## We're authorized; consume no segments
        return (delegate, (), segments)

    def willHandle(self, req):
        return self._get_response_resource(req)
