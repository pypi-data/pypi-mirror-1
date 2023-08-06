
"""
root = {
    'edit': edit.EditDirectory(os.path.dirname(__file__)),
    'tests': testconsole.TestConsole({}, {'host':'localhost'}),
    'cube': cube.Cube(),
    #'twitter': twitter.Twitter([]),
    'hello': hello_pantheon.Hello(),
    'jira': jira.JiraContainer(),
    'testclient': testclient.LoginScreen(),
    'draw': draw.Draw(),
    'login': login.Login(),
    #'debug':debugconsole.DebugConsole({}, {})  # still broken  :-(
}
"""

#root['shell'] = shellconsole.ShellConsole({}, {'host':'localhost', 'root':root})


def index(req):
    from mulib import mu
    from os import path
    from glob import glob

    base = req.full_url()

    def globit():
        directory = path.dirname(__file__) + '/*.py'
        for app in glob(directory):
            app = path.splitext(path.basename(app))[0]
            if not app.startswith('_'):
                yield app

    return mu.html[
        mu.head[
            mu.link(type="text/css", href=""),
            mu.title["muex: mulib examples"]],
        mu.body[
            mu.h1["Welcome to the mulib examples"],
            mu.ul[
                [mu.li[
                        mu.a(href=base + app)[app]]
                    for app in globit()]
                ]]]


hello = 'world'

