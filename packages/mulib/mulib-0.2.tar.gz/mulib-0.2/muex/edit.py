
from mulib import mu, pantheon, stacked

from os import path

import os
import uuid

from eventlet import jsonhttp


class EditDirectory(mu.Resource):
    def __init__(self, directory):
        self._editors = {}
        self._directory = directory
        
    def childFactory(self, req, name):
        if name == '':
            return self
        try:
            return self._editors[name]
        except KeyError:
            print "FULL URL", req.full_url()
            self._editors[name] = Edit(os.path.join(self._directory, name), req.full_url())
            self._editors[name].read_file()
            return self._editors[name]

    def handle_get(self, req):
        url = req.full_url()
        if not url.endswith('/'):
            url += '/'
            req.response(301, headers=(('Location', url), ), body=url)
            return

        files = os.listdir(self._directory)
        files.sort()
        response = mu.tags.ol()
        for fl in files:
            response[
                mu.tags.li[
                    mu.tags.a(href=url + fl)[fl]]]
        req.write(response)


class Edit(pantheon.Pantheon):
    def __init__(self, filename, baseurl):
        self._filename = filename
        self._baseurl = baseurl
        self.lines = {}
        self.users = {}
        data = {'user': self.users, 'line': self.lines}
        shape = {'user': {str: str}, 'line': {str: dict}}
        pantheon.Pantheon.__init__(
            self, data, shape,
            script=pantheon.sibling(__file__, 'edit.js'),
            stylesheet=pantheon.sibling(__file__, 'edit.css'))

    def read_file(self):
        filename = self._filename

        lines = open(filename).readlines()

        for lineno, line in enumerate(lines):
            self.lines[str(lineno)] = line
            self.notify('PUT', ['line', str(lineno)], {'line': line})

    def consume_edit(self, req, segs):
        if segs == ['login'] and req.method() == 'POST':
            body = req.read_body()
            uid = uuid.uuid4()
            url_parts = req.full_url().split('/')
            url_parts[-1] = 'user'
            url_parts.append(str(uid))
            body['user_url'] = '/'.join(url_parts)
            self.users[str(uid)] = body
            self.notify('PUT', ['user', str(uid)], body)

            req.response(200)
            req.write(body)
            return
        
        pantheon.consume_pantheon(self, req, segs)


stacked.add_consumer(Edit, Edit.consume_edit)


index = EditDirectory(path.split(__file__)[0])

