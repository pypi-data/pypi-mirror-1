"""\
@file mu
@author Donovan Preston

What does mu mean?

Nothing

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

import cgi
import mimetypes
import os
import simplejson
import sys
import time
import traceback


from eventlet import api, httpd, httpdate


from mulib import stacked
from mulib import htmlexception


class raw(object):
    """An object which contains only xml bytes.
    """
    def __init__(self, string):
        self.string = str(string)

    def __str__(self):
        return self.string


xml = raw


class slot(object):
    """A marker which will be removed in rendering unless it
    is filled by calling stan.fill(name, value), in which case
    value will be rendered in it's place.
    """
    def __init__(self, name):
        self.slot = name
        self.show = ''

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError, name
        return type(self)(name)

    def __iter__(self):
        return iter(())

    def clone(self):
        return type(self)(self.slot)

    def __repr__(self):
        return "slot(%r, %r)" % (self.slot, self.show)


def find(someStan, targetPattern):
    """Find a node marked with the given pattern, "targetPattern",
    in a DOM object, "someStan". Return a clone of it.
    """
    if isinstance(
        someStan, type(pattern)) and someStan.pattern == targetPattern:
        return type(pattern)('', clone_children(someStan.children))
    for child in getattr(someStan, 'children', ()):
        result = find(child, targetPattern)
        if result is not None:
            return result


def rfill(s, **kw):
    if isinstance(s, type(pattern)): return ''
    slot = getattr(s, 'slot', None)
    if slot in kw and not s.show:
        s.show = kw[slot]
    else:
        for child in (getattr(s, 'children', ())):
            rfill(child, **kw)


def fill(s, **kw):
    """Fill all slots below the given stan node,
    s, with the keyword arguments given. Eg:

    foo = ['foo ', slot.bar]

    fill(foo, bar='bar')

    Will ultimately render as "foo bar"
    """
    children = clone_children(s.children)
    for child in children:
        rfill(child, **kw)
    return type(pattern)('', children)


class pattern(object):
    """A marker which lets you find this branch of the tree
    again later.
    """
    def __init__(self, name, children=()):
        self.pattern = name
        if name:
            self.show = ''
        self.children = children

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError, name
        return type(self)(name)

    def __getitem__(self, args):
        if not isinstance(args, (tuple, list)):
            args = (args, )
        return type(self)(
            self.pattern, [x for x in self.children] + list(args))

    def clone(self):
        return type(self)(
            self.pattern, clone_children(self.children))

    fill = fill
    find = find

    def __repr__(self):
        return "pattern(%r, %r)" % (
            self.pattern, self.children)


class attr(object):
    def __init__(self, name, children):
        self.name = name
        self.children = children

    def clone(self):
        if isinstance(self.children, basestring):
            children = self.children
        else:
            children = clone_children(self.children)
        return type(self)(self.name, children)

    def __repr__(self):
        return "attr(%r, %r)" % (
            self.name, self.children)


def clone_children(children):
    new_children = []
    for child in children:
        if hasattr(child, 'clone'):
            new_children.append(child.clone())
        elif isinstance(child, (list, tuple)):
            new_children.append(clone_children(child))
        else:
            new_children.append(child)
    return new_children


class stan(object):
    def __init__(
        self, tag, children, clone=False):
        (self.tag, self.children, self.clone_me) = (
            tag, children, clone)

    def __getitem__(self, args):
        """Add child nodes to this tag.
        """
        if not isinstance(args, (tuple, list)):
            args = (args, )

        if self.clone_me:
            return type(self)(
                self.tag, clone_children(self.children) + list(args), False)

        self.children.extend(args)
        return self

    def __call__(self, **kw):
        """Set attributes of this tag.
        """
        if self.clone_me:
            attrs = [
                attr(k, v)
                for (k, v) in kw.items()]

            children = clone_children(self.children)

            return type(self)(
                self.tag, attrs + children, False)

        for (k, v) in kw.items():
            self.children.insert(0, attr(k, v))
        return self

    def clone(self):
        return type(self)(
            self.tag, clone_children(self.children), True)

    def __repr__(self):
        return "stan(%r, %r, clone=%r)" % (
            self.tag, self.children, self.clone_me)

    find = find



def tag_factory(tagName):
    return stan(tagName, [], True)


inline_elements = [
    'a', 'abbr', 'acronym', 'b', 'basefont', 'bdo', 'big', 'br', 'cite',
    'code', 'dfn', 'em', 'font', 'i', 'img', 'input', 'kbd', 'label',
    'q', 's', 'samp', 'select', 'small', 'span', 'strike', 'strong',
    'sub', 'sup', 'textarea', 'tt', 'u', 'var', 'pre']
inline_elements = dict([(x, True) for x in inline_elements])


singleton_elements = {}


tags_to_create = [
'a','abbr','acronym','address','applet','area','b','base','basefont','bdo',
'big','blockquote','body','br','button','caption','center','cite','code',
'col','colgroup','dd','dfn','div','dl','dt','em','fieldset','font','form',
'frame','frameset','h1','h2','h3','h4','h5','h6','head','hr','html','i',
'iframe','img','input','ins','isindex','kbd','label','legend','li','link',
'menu','meta','noframes','noscript','ol','optgroup','option','p','param',
'pre','q','s','samp','script','select','small','span','strike','strong',
'style','sub','sup','table','tbody','td','textarea','tfoot','th','thead',
'title','tr','tt','u','ul','var'
]


class tags(object):
    """A namespace for tags, so one can say "from mulib.mu import tags"
    and have access to all tags as tags.html, tags.foo, etc
    """
    pass


for tag in tags_to_create:
    T = tag_factory(tag)
    globals()[tag] = T
    setattr(tags, tag, T)
del tag
del T
del tags_to_create


nothing = xml('')


class NotImplementedException(object):
    pass


not_implemented = NotImplementedException()



slot = slot('')
pattern = pattern('')


def safe_load(what):
    if not what:
        return None
    return simplejson.loads(what)


default_parsers = {
            ## TODO mime encoded
            'application/x-www-form-urlencoded': cgi.parse_qs,
            'application/json': safe_load}

def add_parser(parser, mime_type):
    """ Adds a parser for a particular mime type to the default
    parsers.  This is used when calling request.parsed_body()."""
    default_parsers[mime_type] = parser

class SiteMap(object):
    def __init__(self, root=None):
        if root is None:
            root = {}
        if isinstance(root, Resource):
            root.child_ = root
        self.root = root
        self.parsers = default_parsers.copy()

    def handle_request(self, req):
        if not hasattr(req, 'context'):
            ## Gag me with a spoon
            req.context = {}
        req.site = self
        req.remaining = ()
        try:
            segments = req.path_segments()
            #api.spew()
            stacked.consume(self.root, req, segments)
            #api.unspew()
        except httpd.ErrorResponse, err:
            req.response(code=err.code,
                             reason_phrase=err.reason,
                             headers=err.headers,
                             body=err.body)
        except Exception,e:
            import sys, traceback
            (typ,val,tb) = sys.exc_info()
            traceback.print_exception(Exception,e,tb)
            traceback.print_exc(file=req.protocol.server.log)
            #api.unspew()
            if not req.response_written():
                req.response(code=500, body=htmlexception.format_exc())
            traceback.print_exc()

    def adapt(self, obj, request):
        if getattr(obj, '_implements_mu_resource', False):
            result = obj.willHandle(request)
            if result is not None:
                obj = result
            try:
                obj.handle(request)
            finally:
                obj.afterHandle(request)
            return

        accept_header = request.get_header('accept', '').strip()
        if not hasattr(request, '_cached_acceptable'):
            acceptable = []
            for candidate in accept_header.split(','):
                stuff = candidate.split(';')
                media_type = stuff.pop(0).strip()
                if stuff:
                    params = dict(
                        [x.split('=', 1) for x in stuff])
                else: 
                    params = dict(q=1)
                acceptable.append((float(params.get('q',0)), media_type))

            acceptable.sort()
            acceptable.reverse()
            acceptable.insert(0, (1, request.get_header('content-type')))
            request._cached_acceptable = acceptable

        acceptable = request._cached_acceptable
        for (_, media_type) in acceptable:
            if (media_type in stacked._producer_adapters
                and type(obj) in stacked._producer_adapters[media_type]):
                if media_type != '*/*':
                    request.set_header('content-type', media_type)
                stacked._producer_adapters[media_type][type(obj)](obj, request)
                return
            
        if accept_header:
            # unacceptable accept headers, client!
            request.protocol.server.log.write("Unacceptable from %s: %s" % (request.socket, accept_header))
            raise httpd.ErrorResponse(406)

        if type(obj) not in stacked._producer_adapters['*/*']:
            raise stacked.NoProducer, "No producer added for type %s (%s); browser requested accept %s; available %s. (*/*: %s)" % (
                type(obj), obj, acceptable, stacked._producer_adapters.keys(), stacked._producer_adapters['*/*'].keys())

        ## No accept header; use the */* adapter, assume it's a browser wanting html
        request.set_header('content-type', 'text/html')
        stacked._producer_adapters['*/*'][type(obj)](obj, request)
        return


class Resource(object):
    _implements_mu_resource = True
    debug = False
    content_type = 'text/html'
    template = not_implemented

    def __call__(self, request, name):
        return self

    def afterHandle(self, request):
        """This resource was on the path to the eventual handling
        of the request.  Called after the request was actually handled."""
        pass

    def willHandle(self, request):
        """This Resource is about to handle a request.
        If it wants to delegate to another Resource, it can return it here.
        """
        return self

    def findChild(self, request, segments):
        """External URL segment traversal API. This method MUST always
        return a tuple of:

            (child, handled, remaining)

        child may be None to indicate a 404. Handled should be a tuple
        of URL segments which were handled by this call to findChild;
        remaining should be a tuple of URL segments which were not
        handled by this call to findChild.

        findChild can be overriden to implement fancy URL traversal
        mechanisms such as handling multiple segments in one call,
        doing an internal server-side redirect to another resource and
        passing it segments to handle, or delegating this segment
        to another resource entirely. However, for most common use
        cases, you will not override findChild.

        Any methods or attributes named child_* will be mapped to
        URL segments. For example, if an instance of Root is set
        as the root object, the urls "/foo" and "/bar" will be valid:

        class Root(Resource):
            child_foo = Resource()

            def child_bar(self, request, bar):
                return Resource()

        Finally, if a childFactory method is defined it will be called
        with a single URL segment:

        class Root(Resource):
            def childFactory(self, request, childName):
                ## For URL "/foo" childName will be "foo"
                return Resource()
        """
        ## Refresh our code
        selfType = type(self)
        if self.debug and selfType.__module__ != '__main__':
            self.__class__ = getattr(
                reload(sys.modules[selfType.__module__]), selfType.__name__)

        current, remaining = segments[0], segments[1:]
        childFactory = getattr(self, 'child_%s' % (current, ), self.childFactory)
        return childFactory(request, current), (current, ), remaining

    def childFactory(self, request, childName):
        """Override this to produce instances of Resource to represent the next
        url segment below self. The next segment is provided in childName.
        """
        return None

    def handle(self, request):
        ## Refresh our code
        selfType = type(self)
        if self.debug and selfType.__module__ != '__main__':
            self.__class__ = getattr(
                reload(sys.modules[selfType.__module__]), selfType.__name__)

        ## Handle the request
        request['Content-Type'] = self.content_type
        handler = getattr(
            self,
            "handle_%s" % (request.method().lower(), ),
            self.handle_default)
        handler(request)

    def handle_default(self, request):
        """ Called for HTTP methods that don't have a handle_<method> method. """
        request.write(not_implemented)

    def handle_head(self, request):
        """ Override this to implement HEAD. The default implementation just
        calls handle_get without writing a body."""
        def noop(*_args):
            pass
        temp_write = request.write
        try:
            request.write = noop
            self.handle_get(request)
        finally:
            request.write = temp_write
            request.write('')  # never send a body, even if there's an exception

    def handle_get(self, request):
        """ Override this to implement GET. """
        get_method = self.getAction('get', request.get_field_storage())
        if get_method is None:
            request.write(self.template)
        else:
            try:
                result = get_method(request)
            except TypeError:
                request.protocol.server.log.write("get_method wrong arity: %s" % get_method)
                raise
            request.write(result)

    def handle_delete(self, request):
        """ Override this to implement DELETE. """
        request.write(not_implemented)

    def handle_put(self, request):
        """ Override this to implement PUT. """
        request.write(not_implemented)

    def handle_options(self, request):
        """ Override this to implement OPTIONS. """
        request.write(not_implemented)

    def getAction(self, key, fs):
        if isinstance(fs, dict):
            value = dict.get(key, 'default')
        else:
            try:
                value = fs.getfirst(key, 'default')
            except TypeError:
                value = 'default'
        return getattr(self, '%s_%s' % (key, value), None)

    def handle_post(self, request):
        """ Override this to implement POST. """
        fs = request.get_field_storage()
        post_method = self.getAction('post', fs)
        if post_method is None:
            url = self.post(request, fs)
        else:
            url = post_method(request)

        if url is not None:
            request['Location'] = str(url)
            request.response(303)
            request.write('')
            return
        request.write(self.template)

    def post(self, request, form):
        """post

        Override this to handle a form post.
        Return a URL to be redirected to.

        request: An HttpRequest instance representing the place the form
                  was posted to.
        form: A cgi.FieldStorage instance representing the posted form.
        """
        return request.uri()


def produce_not_implemented(it, req):
    req.response(501)
    req.write({'error': True, 'message': 'Not implemented'})

stacked.add_producer(NotImplementedException, produce_not_implemented, '*/*')
stacked.add_producer(NotImplementedException, produce_not_implemented, 'text/html')
stacked.add_producer(NotImplementedException, produce_not_implemented,
    'application/json')


def produce_raw(it, req):
    req.write(it.string)

stacked.add_producer(raw, produce_raw, '*/*')
stacked.add_producer(raw, produce_raw, 'text/html')
stacked.add_producer(raw, produce_raw, 'application/json')


def produce_pattern(it, req):
    ## Pattern originals left in the template are elided
    if it.pattern:
        req.write(nothing)
        return
    stacked.produce(it.children, req)
stacked.add_producer(type(pattern), produce_pattern, '*/*')
stacked.add_producer(type(pattern), produce_pattern, 'text/html')


def produce_slot(it, req):
    stacked.produce(it.show, req)
stacked.add_producer(type(slot), produce_slot, '*/*')
stacked.add_producer(type(slot), produce_slot, 'text/html')


def produce_stan(it, req):
    attrs = ''
    numattrs = 0
    for att in it.children:
        if not isinstance(att, attr):
            break
        numattrs += 1
        name = att.name
        if name.startswith('_'):
            name = name[1:]
        fake = stacked.TestRequest(req)
        stacked.produce(att.children, fake)
        attrs += ' %s="%s"' % (
            name, fake.result().replace('"', '&quot;'))

    depth = getattr(req, 'depth', 0)
    indent = '  ' * depth
    req.depth = depth + 1
    if (it.tag in singleton_elements and not [
        x for x in it.children[numattrs:] if x]
    ):
        template = """<%(tag)s%(attrs)s />"""
    elif it.tag in inline_elements:
        template = """<%(tag)s%(attrs)s>%(children)s</%(tag)s>"""
    else:
        template = """
%(indent)s<%(tag)s%(attrs)s>
%(indent)s  %(children)s
%(indent)s</%(tag)s>
"""
    fake = stacked.TestRequest(req)
    stacked.produce(it.children[numattrs:], fake)
    result = template % dict(
        indent=indent, tag=it.tag, attrs=attrs,
        children=fake.result().strip())

    req.depth -= 1
    req.write(result)
stacked.add_producer(stan, produce_stan, '*/*')
stacked.add_producer(stan, produce_stan, 'text/html')


def redirect_to_slash(req):
    url = req.full_url()
    if not url.endswith('/'):
        url += '/'
        req.response(301, headers=(('Location', url), ), body=url)
        return True
    return False

