"""@file caps.py

@brief Simple in-memory transient capability store; maps between public urls and private urls.

$LicenseInfo:firstyear=2006&license=mit$

Copyright (c) 2006-2008, Linden Research, Inc.

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
$/LicenseInfo$

TODO
- Expiry

URL namespace:

/cap/grant
/cap/multigrant
/cap/revoke
"""

import atexit
from os import path
import os
import marshal
import sys
import time
import traceback
import uuid

from eventlet import api
from mulib import mu
from mulib import proxy
from mulib import stacked


CAPABILITY_TEMP_FILE = '/tmp/capabilities.tmp'
MAX_TEMP_FILE_AGE = 5 * 60   # 5 minutes


def save_capabilities_to_temp_file(temp_file=CAPABILITY_TEMP_FILE):
    _cap_store.save_to_temp_file(temp_file)

def load_capabilities_from_temp_file(temp_file=CAPABILITY_TEMP_FILE):
    _cap_store.load_from_temp_file(temp_file)


class Capability(object):
    def __init__(self, private, region, key, one_shot, via_cache):
        self.private = private
        self.region = region
        self.key = key
        self.one_shot = one_shot
        self.via_cache = via_cache


_cap_store = None


def capability_store(prefix):
    global _cap_store
    if not _cap_store:
        _cap_store = CapabilityStore(
            prefix)
    return _cap_store


class CapabilityStore(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.capabilities = dict()
        self.load_from_temp_file(CAPABILITY_TEMP_FILE)
        atexit.register(self.save_to_temp_file, CAPABILITY_TEMP_FILE)

    def grant(self, private, region, key, one_shot, via_cache):
        ## Generate a UUID
        while True:
            cap_key = str(uuid.uuid1())

        ## Generate a capability url
        public = '%s%s' % (self.prefix, cap_key, )

        self.capabilities[cap_key] = Capability(
                private, region, key, one_shot, via_cache)

        print "Granted cap:", cap_key, private
        return public

    def invoke(self, public):
        if not public or public not in self.capabilities:
            print "Invoked invalid cap:", `public`
            return None

        cap = self.capabilities[public]
        if cap.one_shot:
            del self.capabilities[public]

        print "Invoked cap:", cap.private
        return cap

    def revoke_by_region(self, revoke_region):
        revoke_cap_keys = [
            cap_key for (cap_key, cap) 
                in self.capabilities.iteritems()
                if cap.region == revoke_region
            ]
        for k in revoke_cap_keys:
            del self.capabilities[k]

    def revoke_by_region_and_key(self, revoke_region, revoke_key):
        revoke_cap_keys = [
            cap_key for (cap_key, cap) 
                in self.capabilities.iteritems()
                if cap.region == revoke_region and cap.key == revoke_key
            ]
        for k in revoke_cap_keys:
            cap = self.capabilities[k]
            print "Revoked cap:", k, cap.private
            sys.stdout.flush()
            del self.capabilities[k]

    def revoke_by_public_url(self, public_url):
        if public_url.startswith(self.prefix):
            revoke_cap_key = public_url[len(self.prefix):]
            del self.capabilities[revoke_cap_key]

    def save_to_temp_file(self, temp_file):
        to_marshal = []
        for key, cap in self.capabilities.iteritems():
            cap_val = dict(
                private=str(cap.private),
                region=str(cap.region),
                key=str(cap.key),
                one_shot=bool(cap.one_shot),
                via_cache=bool(cap.via_cache))
            to_marshal.append((key, cap_val))
        marshal.dump(
            to_marshal,
            file(temp_file, 'wb'))
    
    def load_from_temp_file(self, temp_file):
        if not path.exists(temp_file):
            print "Not loading temporary capabilities; file does not exist",\
                temp_file
            return

        if os.stat(temp_file).st_mtime < time.time() - MAX_TEMP_FILE_AGE:
            print "Temporary file too old, not loading",\
                temp_file
            return

        try:
            caps = marshal.load(file(temp_file))
            print "Loaded %d temporary capabilities." % (len(caps), )
            for cap_name, cap_dict in caps:
                self.capabilities[cap_name] = Capability(**cap_dict)
            os.remove(temp_file)
        except Exception, e:
            print "Could not load temporary capabilities:"
            traceback.print_exc()

    def handle(self, req, segs):
        if segs == ['grant']:
            body = req.parsed_body()

            if 'private-url' not in body:
                return req.response(400, body='Missing private-url')

            public = self.grant(
                body['private-url'],
                body.get('region', ''),
                body.get('key', ''),
                body.get('one-shot', False),
                body.get('via-cache', False))

            return req.write({'public-url': public})
        elif segs == ['revoke']:
            body = req.parsed_body()
            criteria = body.keys()
            criteria.sort()

            if criteria == ['public-url']:
                self.revoke_by_public_url(body['public-url'])
            elif criteria == ['region']:
                self.revoke_by_region(body['region'])
            elif criteria == ['key', 'region']:
                self.revoke_by_region_and_key(body['region'], body['key'])
            else:
                return req.response(400, body='Invalid criteria')

            return req.write(None)
        elif segs == ['multigrant']:
            request = req.parsed_body()
            response = []
            for body in request:            
                if 'private-url' not in body:
                    return req.response(400, body='Missing private-url')

                public = self.grant(
                    body['private-url'],
                    body.get('region', ''),
                    body.get('key', ''),
                    body.get('one-shot', False),
                    body.get('via-cache', False))

                response.append({'public-url': public})

            return req.write(response)


stacked.add_consumer(CapabilityStore, CapabilityStore.handle)


class CapabilityProxy(object):
    console = None
    def __init__(self, caps, verbose=False):
        self.caps = caps
        self.verbose = verbose

    def handle(self, req, segs):
        ## The next url segment below this object
        ## should be the uuid of a capability.
        if len(segs) > 1:
            return req.response(404, body='')

        cap = self.caps.invoke(segs[0])
        if cap is None:
            return req.response(404, body='')

        ## now we need to actually proxy to the destination server
        delegate = proxy.Proxy(
            cap.private, self.console, self.verbose, cap.via_cache)

        try:
            delegate.handle(req)
        except SysCallError, e:
            # 104 == Connection rest by peer. that will just happen
            # from time to time.
            if e[0] != 104:
                raise


stacked.add_consumer(CapabilityProxy, CapabilityProxy.handle)
