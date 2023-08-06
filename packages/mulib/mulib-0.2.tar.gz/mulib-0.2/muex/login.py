
import md5
import xmlrpclib


from mulib import mu, stacked

def login(first, last, key):
    uri = 'https://login.agni.lindenlab.com/cgi-bin/login.cgi'
    s = xmlrpclib.ServerProxy(uri)
 
    login_details = {
        'first': first,
        'last': last,
        'web_login_key': key,
        'start': 'last',
        'channel': 'login.py',
        'version': '0.1',
        'platform': 'lnx',
        'mac': '',
        'options': [],
        'user-agent': 'login.py 0.1',
        'id0': '',
        'agree_to_tos': '',
        'viewer_digest': '09d93740-8f37-c418-fbf2-2a78c7b0d1ea'
        }
    return s.login_to_simulator(login_details)


class Login(object):
    def produce(self, req):
        web_login_key = req.get_arg('web_login_key')
        if web_login_key:
            first = req.get_arg('first_name')
            last = req.get_arg('last_name')
            print "got key", web_login_key, first, last
            login_response = login(first, last, web_login_key)
            print "response", login_response
            sorted = login_response.items()
            sorted.sort()
            response = mu.html[
                mu.body[
                    "Welcome, %s %s!!" % (first, last),
                    mu.table[
                      [mu.tr[mu.td[k], mu.td[v]] for (k, v) in sorted]]]]
            req.set_header('content-type', 'text/html')
            req.write(response)
            return

        req.set_header('content-type', 'text/html')
        req.write(
            mu.html[
                mu.body[
                    "Welcome to the continuation url demo. ",
                    mu.a(href="https://secondlife.com/inworld/?continuation=%s?" % req.full_url())[
                        "Click here to authenticate with secondlife.com."]]])

stacked.add_producer(Login, Login.produce)


index = Login()
