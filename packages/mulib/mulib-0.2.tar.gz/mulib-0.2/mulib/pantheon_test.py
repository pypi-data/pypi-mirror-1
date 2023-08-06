

from eventlet import api
from eventlet import coros
from eventlet import util
from eventlet import jsonhttp

from mulib import tests
from mulib import pantheon


util.wrap_socket_with_coroutine_socket()


class TestPantheon(tests.TestServer):
    def setUp(self):
        tests.TestServer.setUp(self)
        self.site.root['foo'] = self.pan = pantheon.Pantheon()
        #print "setUp", self.pan

    def observe(self, *observation_list):
        def wait_for_event():
            #print "wait"
            result = jsonhttp.post('http://localhost:9000/foo/', {
                'observe': observation_list})
            #print "result", result
            return result

        evt = coros.execute(wait_for_event)
        ## Wait for the server to get the observation request
        #print "waiting", self.pan
        while not self.pan._notify and evt._result is coros.NOT_USED:
            api.sleep(0.01)

        return evt

    def put(self, path, body):
        #print "notify", path, body
        jsonhttp.put(
            'http://localhost:9000/foo/' + '/'.join(path), body)

    def test_00_simple_notify(self):
        evt = self.observe({'path': 'foo'})

        ## Resume the observation request
        self.put(['foo'], 'bar')

        result = evt.wait()

        self.assertEquals(result['body'], 'bar')

    def test_01_observe_after_notify(self):
        self.put(['foo'], 'bar')

        result = jsonhttp.post('http://localhost:9000/foo/', {
            'observe': [
                {'path': 'foo'}]})

        self.assertEquals(result['body'], 'bar')

    def test_02_notify_twice_elides_events(self):
        self.put(['foo'], 'foo')
        self.put(['foo'], 'bar')

        result = jsonhttp.post('http://localhost:9000/foo/', {
            'observe': [
                {'path': 'foo'}]})

        self.assertEquals(result['body'], 'bar')

    def test_03_basic_container_event(self):
        jsonhttp.put('http://localhost:9000/foo/container', {})

        container_event = self.observe({'path': 'container'}).wait()
        self.assertEquals(
            container_event['path'],
            ['container'])

        evt = self.observe({
            'path': 'container/*',
            'etag': container_event['etag']})

        self.put(['container', 'baz'], 'asdf')
        self.assertEquals(evt.wait()['body'], 'asdf')

    def test_04_container_events(self):
        jsonhttp.put('http://localhost:9000/foo/container', {})

        container_event = self.observe({'path': 'container'}).wait()
        self.assertEquals(
            container_event['path'],
            ['container'])

        self.put(['container', 'baz'], 'asdf')
        self.put(['container', 'whop'], 'foom')

        first_event = self.observe({
            'path': 'container/*'}).wait()

        print first_event
        self.assertEquals(first_event['body'], 'asdf')

        second_event = self.observe({
            'path': 'container/*',
            'etag': first_event['etag']}).wait()

        print second_event
        self.assertEquals(second_event['body'], 'foom')

    def test_05_elided_container_events(self):
        jsonhttp.put('http://localhost:9000/foo/container', {})

        container_event = self.observe({'path': 'container'}).wait()
        self.assertEquals(
            container_event['path'],
            ['container'])

        self.put(['container', 'baz'], 'asdf')
        self.put(['container', 'baz'], 'foom')

        first_event = self.observe({
            'path': 'container/*'}).wait()

        self.assertEquals(first_event['body'], 'foom')

    

if __name__ == '__main__':
    tests.main()

