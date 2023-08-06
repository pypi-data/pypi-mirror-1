

import uuid
import xmlrpclib

from eventlet import api
from eventlet import httpc
from eventlet import jsonhttp

from mulib import mu
from mulib import stacked
from mulib import pantheon


POLL_INTERVAL = 60


template = mu.html[
    mu.body[
        mu.form(action='create', method='POST')[
            mu.input(name='username'),
            mu.input(type='password', name='password'),
            mu.input(name='host'),
            mu.input(type='submit')]]]


class JiraContainer(object):
    def __init__(self):
        self.jiras = {}

    def produce(self, req):
        url = req.full_url()
        if not url.endswith('/'):
            return req.response(301, headers={'location': url + '/'}, body='')
        req.write(template)

    def consume(self, req, segs):
        if segs == ['']:
            return self.produce(req)

        method = req.method()
        if segs == ['create'] and method == 'POST':
            body = req.read_body()
            u = str(uuid.uuid1())
            parts = req.full_url().split('/')
            parts[-1] = u
            self.jiras[u] = Jira(dict([(k, v[0]) for (k, v) in body.items()]))
            return req.response(301, headers={'location': '/'.join(parts) + '/'}, body='')
        if segs[0] in self.jiras:
            return stacked.consume(self.jiras[segs[0]], req, segs[1:])
        req.response(404, body='')


stacked.add_producer(JiraContainer, JiraContainer.produce)
stacked.add_consumer(JiraContainer, JiraContainer.consume)


class Jira(pantheon.Pantheon):
    def __init__(self, cred):
        self.running = False
        self.cred = cred
        pantheon.Pantheon.__init__(
            self, {'filters': {}},
            script=pantheon.sibling(__file__, 'jira.js'),
            stylesheet=pantheon.sibling(__file__, 'jira.css'))

    def produce(self, req):
        if not self.running:
            self.running = True
            self.poll_jira_forever(self.cred, req.full_url())
            del self.cred
        pantheon.produce_pantheon(self, req)

    def poll_jira_forever(self, cred, full_url):
        try:
            url = 'https://%s:%s@%s/rpc/xmlrpc' % (cred['username'], cred['password'], cred['host'])
            srv = xmlrpclib.ServerProxy(url)
            token = srv.jira1.login(cred['username'], cred['password'])
            filters = srv.jira1.getSavedFilters(token)
            for fil in filters:
                filter_url = full_url + 'filters/' + fil['id']
                try:
                    jsonhttp.head(filter_url)
                except httpc.NotFound:
                    jsonhttp.put(filter_url, dict(name=fil['name'], author=fil['author']))
        finally:
            from mulib import jira
            reload(jira)
            print "RELOADED"

            self.__class__ = jira.Jira
            api.call_after(POLL_INTERVAL, self.poll_jira_forever, cred, full_url)


stacked.add_producer(Jira, Jira.produce, 'text/html')
stacked.add_producer(Jira, Jira.produce, '*/*')


index = JiraContainer()

