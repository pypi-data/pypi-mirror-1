
import time

from eventlet import api
from eventlet import channel
from eventlet import processes

from mulib import mu
from mulib import pantheon
from mulib import shaped
from mulib import stacked


TEST_CLIENT_LOCATION = '/local/donovan/libsl/bin/TestClient.exe'


login_form = mu.html[
#    mu.form(action='login')[
#        "Use second life's web login key authentication:",
#        mu.input(name="username"), mu.input(name="lastname"), mu.input(type="submit")
#    ],
    mu.form(action='login')[
        mu.input(name="username"), mu.input(name="lastname"), mu.input(type="password", name="password"), mu.input(type="submit")
    ]
]


class LoginScreen(object):
    def __init__(self):
        self._sessions = {}

    def produce_loginscreen(self, req):
        if mu.redirect_to_slash(req):
            return

        if req.method() == 'GET':
            return req.write(login_form)

        req.response(405, body={}) ## Not Allowed

    def consume_loginscreen(self, req, segs):
        if segs == ['']:
            return stacked.produce(self, req)

        if segs == ['login']:
            if req.method() == 'GET':
                web_login_key = req.get_query('web_login_key')
                password = req.get_query('password')
                session = None
                if web_login_key:
                    session = TestClient(
                        req.get_query('username'),
                        req.get_query('lastname'),
                        web_login_key)
                elif password:
                    web_login_key = str(time.time())
                    session = TestClient(
                        req.get_query('username'),
                        req.get_query('lastname'),
                        password=password)

                if session is not None:
                    self._sessions[web_login_key] = session
                    url_pieces = req.full_url().split('/')
                    url_pieces[-1] = web_login_key
                    new_url = '/'.join(url_pieces)
                    print "new url", new_url
                    req.set_header('location', new_url)
                    req.response(303)
                    req.write({})
                    return                
                req.set_header('location',
                               'http://icehouse.webdev.lindenlab.com/inworld/index.php?continuation=http://station5:8080/testclient/login?username=' +
                               req.get_arg('username') + '%26lastname=' +
                               req.get_arg('lastname') + '%26web_login_key=')
                return req.response(303, body={})

        ## Maybe the next url segment is a session
        stacked.consume(self._sessions, req, segs)


stacked.add_producer(LoginScreen, LoginScreen.produce_loginscreen)
stacked.add_producer(LoginScreen, LoginScreen.produce_loginscreen, 'text/html')
stacked.add_consumer(LoginScreen, LoginScreen.consume_loginscreen)


class TestClient(pantheon.Pantheon):
    def __init__(self, username, lastname, web_login_key=None, password=None, loginuri=None, test_client_location=None):
        pantheon.Pantheon.__init__(self, {'line': []}, script=pantheon.sibling(__file__,'testclient.js'))
        if test_client_location is None:
            test_client_location = TEST_CLIENT_LOCATION

        args = [test_client_location, '--first', username, '--last', lastname]
        if web_login_key:
            args.extend(['--loginkey', web_login_key])
        else:
            args.extend(['--pass', password])
        if loginuri is not None:
            args.append('--loginuri="' + loginuri + '"')
        self.input_channel = channel.channel()

        proc = processes.Process('mono', args)

        self.reader = api.spawn(self.read_process_forever, proc)
        self.writer = api.spawn(self.write_process_forever, proc)

    def read_process_forever(self, read):
        while True:
            line = read.readline()
            if not line:
                api.sleep(0.5)
                continue
            print "LINE", line
            all_lines = self._data['line']
            next_line_no = str(len(all_lines))
            all_lines.append(line)
            self.notify('PUT', ['line', str(len(all_lines))], line)

    def write_process_forever(self, write):
        while True:
            send_to_client = self.input_channel.receive()
            write.write(send_to_client + '\n')

    def consume_testclient(self, req, segs):
        method = req.method()
        if method == 'POST' and segs == ['input']:
            self.input_channel.send(req.read_body())
            req.write({})
            return
        pantheon.consume_pantheon(self, req, segs)


stacked.add_consumer(TestClient, TestClient.consume_testclient)


index = LoginScreen()

