
import time
import datetime
import traceback
import os.path

from eventlet import api
from eventlet import coros
from eventlet import jsonhttp
from eventlet import httpc

from mulib import pantheon
from mulib import stacked

APP_ROOT = "http://donovanpreston.com:8080/twitter/"

SELF_FOLLOWING = APP_ROOT + "following"
SELF_TEMPLATE = APP_ROOT + "users/%s/%s"
FOLLOW_TEMPLATE = "http://twitter.com/statuses/user_timeline/%s.json"
SLEEP_INTERVAL = 60 * 2


the_pool = coros.CoroutinePool(max_size=64)


class Twitter(pantheon.Pantheon):
    SLEEP_INTERVAL = SLEEP_INTERVAL
    my_pool = the_pool
    def __init__(self, follow_usernames):
        self._sleep_interval = self.SLEEP_INTERVAL
        self._twitter_etags = {}
        api.spawn(self.start_following, follow_usernames)

        data = {'following': [], 'users': {}}
        shape = {'following': [], 'users': {str: {str: str}}}
        pantheon.Pantheon.__init__(
            self, data,
            script=pantheon.sibling(__file__, 'twitter.js'),
            stylesheet=pantheon.sibling(__file__, 'twitter.css'))

    def start_following(self, follow_usernames):
        if getattr(self, '_following_started', None) is not None:
            return

        self._following_started = True

        jsonhttp.put(SELF_FOLLOWING, follow_usernames)

        while True:
            self.fetch_all_users()
            print "sleeping %s" % (self._sleep_interval, )
            api.sleep(self._sleep_interval)

    def fetch_all_users(self):
        waiters = []
        for follow_username in self._data['following']:
            self.my_pool.execute_async(
                self.fetch_user, follow_username)

    def fetch_user(self, follow_username):
        follow_directory = os.path.dirname(
            SELF_TEMPLATE % (follow_username, ''))
        try:
            print "following %s" % (follow_username, )
            jsonhttp.head(follow_directory)
        except httpc.NotFound:
            print "creating directory"
            jsonhttp.put(follow_directory, {})
        follow_url = FOLLOW_TEMPLATE % follow_username
        try:
            start_time = time.time()
            if follow_username in self._twitter_etags:
                print "using etag", follow_username, self._twitter_etags[follow_username]
                code, headers, message = jsonhttp.get_(
                    follow_url,
                    {'If-None-Match': self._twitter_etags[follow_username]})
            else:
                code, headers, message = jsonhttp.get_(
                    follow_url)

            self._twitter_etags[follow_username] = headers.getheader('etag')
            print "(%.6fs) %s %s" % (
                time.time() - start_time,
                len(message), follow_url)
            for result in message:
                result['created_time'] = time.mktime(time.strptime(
                    result['created_at'], "%a %b %d %H:%M:%S +0000 %Y"))
                print "CREATED_TIME", result['created_time']
                text = result['text']
                result_id = result['id']
                result_url = SELF_TEMPLATE % (
                    result['user']['screen_name'], result_id)
                print "result", result_url
                try:
                    jsonhttp.head(result_url)
                except httpc.NotFound:
                    jsonhttp.put(result_url, result)
        except httpc.NotModified:
            print "%s: Not Modified" % (follow_username, )
        except Exception, e:
            print "Exception while following %s (%s); skipping" % (
                follow_username, follow_url)
            traceback.print_exc()

    def consume_twitter(self, req, segs):
        if segs == ['following']:
            if req.method() == 'PUT':
                old_usernames = dict(
                    [(x, True) for x in self._data['following']])
                for new_name in req.read_body():
                    if new_name not in old_usernames:
                        self.my_pool.execute_async(self.fetch_user, new_name)
        pantheon.consume_pantheon(self, req, segs)


stacked.add_consumer(Twitter, Twitter.consume_twitter)


index = Twitter([])

