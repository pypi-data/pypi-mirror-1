"""\
@file virtual.py
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


from mulib import mu


class RedirectToHost(mu.Resource):
    def __init__(self, host):
        self.host = host

    def findChild(self, req, seg):
        return self, seg, ()

    def handle(self, req):
        req.response(301)
        path = req.path()
        query = req.query()
        if query:
            path = path + '?' + query

        ## TODO: Support https
        req.set_header('Location', 'http://%s%s' % (self.host, path))
        req.write('')


class VirtualHost(mu.Resource):
    default = None
    def __init__(self):
        """A Resource which delegates the request based on the
        Host header to the appropriate root resource.

        Hosts are registered by calling set_host, passing a host
        name and the host root resource.
        """
        self.hosts = {}

    def set_host(
        self, host_name, host_root, respond_to_www=True, default=True):
        """Set the root resource, host_root, to use
        for the host host_name.

        If respond_to_www is True, also set this host_root
        as the root resource of 'www.' + host_name, if host_name
        does not already start with 'www.'

        If default is True, this resource will be used if there is no
        host which matches the Host header given in the request.
        """
        if getattr(host_root, '_implements_mu_resource', False):
            host_root.child_ = host_root
        self.hosts[host_name.lower()] = host_root
        if respond_to_www:
            if not host_name.startswith('www.'):
                self.hosts[host_name.lower()] = RedirectToHost(
                    'www.' + host_name)
                self.hosts['www.' + host_name] = host_root
        if default:
            self.default = host_root

    def findChild(self, req, segments):
        """VirtualHost implementation.
        """
        return (
            self.hostFactory(req, req.get_header('host', '')),
            (),
            segments)

    def hostFactory(self, req, host):
        """Override this if you wish to specify what will happen
        if there is no registered host which matches the current
        request's Host header
        """
        return self.hosts.get(host.lower(), self.default)


