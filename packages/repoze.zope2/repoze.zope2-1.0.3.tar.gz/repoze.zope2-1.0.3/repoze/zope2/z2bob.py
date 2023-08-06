##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

""" An obob plugin which implements Zope2 ZPublishing publishing semantics """


from cgi import escape
import inspect
import re
import threading
import urlparse
import urllib
import xmlrpclib

from paste import httpexceptions
from paste import httpheaders

from zope.component import queryMultiAdapter
from zope.interface import Interface

from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher
try:
    # 2.10+ 
    from zope.publisher.browser import setDefaultSkin
except ImportError:
    # 2.9
    from zope.app.publication.browser import setDefaultSkin

from zope.security.management import newInteraction
from zope.security.management import endInteraction

try:
    # 2.10+
    from zope.traversing.namespace import nsParse
except ImportError:
    # 2.9
    from zope.app.traversing.namespace import nsParse

try:
    # 2.10+
    from zope.traversing.namespace import namespaceLookup
except ImportError:
    from zope.app.traversing.namespace import namespaceLookup

try:
    # 2.10 +
    from zope.traversing.interfaces import TraversalError
except ImportError:
    # 2.9
    from zope.app.traversing.interfaces import TraversalError

from AccessControl.ZopeSecurityPolicy import getRoles
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import Unauthorized as AccessControl_Unauthorized

# we still import these because they're compared using 'is' outside ZPublisher
from ZPublisher.BaseRequest import RequestContainer
from ZPublisher.BaseRequest import UNSPECIFIED_ROLES
from ZPublisher.xmlrpc import Response as XMLRPCResponse

from zExceptions import Unauthorized
from zExceptions import Redirect

import transaction
from repoze.tm import after_end
from repoze import tm

from repoze.zope2.mapply import mapply
from repoze.zope2.mapply import dont_publish_class
from repoze.zope2.mapply import missing_name
from repoze.zope2.publishtraverse import DefaultPublishTraverse
from repoze.zope2.publishtraverse import _BETTER_THAN_210
from repoze.zope2.request import makeRequest
from repoze.zope2.request import convertResponseCode
from repoze.zope2.db import getDB

_FALSETYPES = (None, 0, False, '', u'')
_UNAUTH_CLASSES = (Unauthorized, AccessControl_Unauthorized)

def quote(text):
    # quote url path segments, but leave + and @ intact
    return urllib.quote(text, '/+@')

def cleanPath(path):
    # Cleanup the path list
    if path[:1]=='/':
        path=path[1:]
    if path[-1:]=='/':
        path=path[:-1]
    clean=[]
    for item in path.split('/'):
        # Make sure that certain things that dont make sense
        # cannot be traversed.
        if item in ('REQUEST', 'aq_self', 'aq_base'):
            # ZPublisher used to do NotFound, but that's wrong
            raise httpexceptions.HTTPForbidden(path)
        if not item or item=='.':
            continue
        elif item == '..':
            del clean[-1]
        else:
            clean.append(item)
    return clean

def exec_callables(callables):
    result = None
    for (f, args) in callables:
        # Don't catch exceptions here. And don't hide them anyway.
        result = f(*args)
        if result is not None:
            return result

base_re_search=re.compile('(<base.*?>)',re.I).search
start_of_header_search = re.compile('(<head[^>]*>)', re.IGNORECASE).search

def asbool(v):
    if isinstance(v, bool):
        return v
    if v.strip().lower() in ('true', '1', 'on', 'yes'):
        return True
    return False

class Zope2ObobHelper:
    def __init__(self, environ, **config):
        self._configure(config)
        self.environ = environ
        self.request = None
        self.root = None
        self.conn = None
        self.browser_default = False
        self.browser_default_published = None
        self.method_default = False
        self.user_folders = []
        self.traversed = []
        self.default_page = 'index_html'
        self.vroot_stack = None

    def _configure(self, config):
        self._config = config
        self.encoding = config.get('encoding', 'utf-8')
        self.appname = config.get('appname', 'Application')
        self.browser_default_redirects = asbool(config.get(
            'browser_default_redirects', False))

    def __del__(self):
        if tm and not tm.isActive(self.environ):
            errors = self.environ.get('wsgi.errors')
            try:
                self.conn.close()
                msg ='repoze.tm not active; transaction uncommitted\n'
                errors and errors.write(msg)
            except:
                pass

    def setup(self):
        self.vroot_stack = None
        from repoze.vhm.utils import setServerURL
        
        # dictate what SERVER_URL is instead of allowing the request
        # constructor to compute it
        setServerURL(self.environ) 
        request = makeRequest(self.environ)
        request._resetURLS()
        request.no_acquire_flag = False
        setDefaultSkin(request) # analogue of Publish.publish_module_standard
        newInteraction() # analogue of Publish.publish
        request.processInputs() # analogue of Publish.publish
        request_method = request.get('REQUEST_METHOD', 'GET').upper()

        response = request.response
        isxmlrpc = isinstance(response, XMLRPCResponse)

        if isxmlrpc:
            self.default_page = request_method

        elif request_method not in ('GET', 'POST'):
            # This is probably a WebDAV client.  For WebDAV methods,
            # we need to look up the name of the request method as the
            # default page instead of 'index_html'
            request.no_acquire_flag = True # used by DefaultPublishTraverse
            self.default_page = request_method

        if request._hacked_path:
            # the request body contained a method name or form action,
            # which is a special case of a browser default; we need to
            # insert base tag.
            self.method_default = True
        noSecurityManager() # analogue of __bobo_before__
        request._post_traverse = []
        request['PARENTS'] = []
        # do not use environ['PATH_INFO'], processInputs munges it
        self.browser_path = path = request['PATH_INFO']
        
        # Record virtual URL in request if set by repoze.vhm
        virtual_url = self.environ.get('repoze.vhm.virtual_url')
        if virtual_url:
            server_url = request.get('SERVER_URL', '')
            virtual_url_path = quote(virtual_url[len(server_url):])
            
            request['VIRTUAL_URL'] = server_url + virtual_url_path
            request['VIRTUAL_URL_PARTS'] = [server_url] + virtual_url_path.split('/')[1:]
        
        # Set ACTUAL_URL. This is either the server URL with the path
        # appended, or the VIRTUAL_URL if that is set.
        request['ACTUAL_URL'] = self._getActualURL(request)
        
        # Set PATH_TRANSLATED. This is the "real" path to the published
        # item.
        request['PATH_TRANSLATED'] = self._getPathTranslated(request)
        
        request.steps = request._steps = []
        path = self._setVirtualRoot(self.environ, path)
        
        self.clean = cleanPath(path)
        # We need to continue respecting this silly stack to account
        # for hooks that modify it
        trns = self.clean[:]
        trns.reverse()
        request.path = request['TraversalRequestNameStack'] = trns
        request.roles = getRoles(None, None, self.root, UNSPECIFIED_ROLES)
        self.request = request

    def teardown(self):
        endInteraction()
        if self.request is not None:
            # if there was not an error during setup()
            self.request.close()
            # get rid of reference to response in case the request is leaked
            # because a RepozeHTTPResponse holds on to a NamedTemporaryFile.
            self.request.response = None 

        # It's very important to call noSecurityManager() here;
        # otherwise we'll leak as many references to AccessControl
        # SecurityManager objects as there are threads in the WSGI
        # server's worker thread pool.  These will hold references to
        # aq-wrapped user objects, which in turn hold references to
        # "the world".  It doesn't matter that we also call
        # noSecurityManager in setup() because that might be in a
        # different thread and we really need to clear *this* thread's
        # security manager now to avoid a leak.  In fact, the call in
        # setup() is probably voodoo.
        noSecurityManager() 

        # Be tediously explicit about clearing out references; if we
        # get leaked for some reason, we really don't want our
        # subitems hanging around.  But we can't yet get rid of
        # environ or conn as they're used in __del__ :-(
        self.request = None
        self.user_folders = None
        self.vroot_stack = None
        self.root = None
        self.browser_default_published = None

    def next_name(self):
        trns = self.request['TraversalRequestNameStack']

        if trns:
            name =  trns.pop()
            if name.startswith('_rvh:') and self.vroot_stack is not None:
                # this is a repoze.vhm.virtual_root-defined name; pop
                # it off the vroot stack too; when the vroot stack is
                # empty, we'll be able to set VirtualRootPhysicalPath
                # in the request.
                self.vroot_stack.pop()
                name = name[len('_rvh:'):]
            return name

        else:
            # we've reached the end of the non-default stack; we've
            # found our published object as per the URL path, but now
            # we need to return a browser default name iff the
            # published object has any attribute by that name
            parents = self.request['PARENTS']
            published = parents[-1]

            default_page = self.default_page

            adapter = self._getPublishTraverseView(IBrowserPublisher, published)
            default, path = adapter.browserDefault(self.request)

            if default is not published:
                self.browser_default = True
                self.browser_default_published = default
                published = default

            if path:
                # __browser_default__ can return any number of names
                # in its second return value (which must be a
                # sequence).  But this doesn't work as advertised in
                # the original ZPublisher BaseRequest.traverse because
                # it pops the last name off the path as the "method",
                # then stuffs the remainder of the items in the path
                # into TraversalRequestNameStack *in the wrong order*
                # (discovered via empirical testing).  E.g. if you
                # return ('a', 'b', 'c') from your __browser_default__
                # method, 'c' is popped off and chosen as the
                # 'method', then TraversalRequestNameStack is set to
                # ['a', 'b'].  But this is just wrong, because the
                # trns *should* be ['b', 'a'] given how
                # BaseRequest.traverse pops names off the stack (from
                # back to front).  Since this doesn't appear to make
                # sense under ZPublisher "proper", we just ignore all
                # but the last element of the returned path and use it
                # as the default_page.  Code that depended on
                # returning more than two names and which worked
                # around the reversed-order bug will lose, sorry.
                self.browser_default = True
                default_page = path[-1]

            # we need to check if we actually have a default page in
            # next_name because if we try to do it in traverse, if we
            # don't actually *have* the default page (because we've
            # already traversed it explicitly, for example), we'll be
            # "stuck" redoing the before_traverse of the previous
            # object and cleaning up the URL and such.
            if self._hasDefaultPage(published, default_page):
                return default_page

    def before_traverse(self, ob):
        # NB: we *must* build the PARENTS list in "reverse" order then
        # re-reverse it within before_invoke.  This is particularly
        # true when using VirtualHostMonster, which assumes this
        # particular ordering during its __bobo_traverse__ (it pops
        # itself from PARENTS, then pops the published object from
        # PARENTS, and returns it).
        self.request['PARENTS'].append(ob)

        bpth = getattr(ob, '__before_publishing_traverse__', None)
        if bpth is not None:
            bpth(ob, self.request)

    def traverse(self, ob, name):
        if self.browser_default_published is not None:
            # __browser_default__ replaced the published object with
            # another (the first argument returned a different object)
            ob = self.browser_default_published

        self._userFolderInsert(ob)

        request = self.request

        url = self.request['URL']
        if not url.endswith('/'):
            url = url + '/'
        self.request['URL'] = urlparse.urljoin(url, quote(name))
        self.request.steps.append(quote(name))
        request._resetURLS()

        ob2 = None

        if name and name[:1] in '@+':
            # Process URI segment parameters.
            ns, nm = nsParse(name)
            if ns:
                try:
                    ob2 = namespaceLookup(ns, nm, ob, request)
                except TraversalError:
                    raise httpexceptions.HTTPNotFound(name)
                ob2 =  ob2.__of__(ob)


        if ob2 is None:
            adapter = self._getPublishTraverseView(IPublishTraverse, ob)
            try:
                ob2 = adapter.publishTraverse(request, name)
            except (KeyError, AttributeError, TraversalError,):
                raise httpexceptions.HTTPNotFound(name)

        request.roles = getRoles(ob, name, ob2, request.roles)
        self.traversed.append(name)

        if self.vroot_stack is not None:
            # there was a virtual root specified during this request
            # (via 'repoze.vhm.virtual_root')
            if not self.vroot_stack:
                # the virtual root stack has been popped until empty,
                # which means the object we just traversed is the
                # virtual root; set its physical path in
                # request.other's VirtualRootPhysicalPath.
                request.other['VirtualRootPhysicalPath'] = ob2.getPhysicalPath()
                # clear _steps: URLs computed subsequently won't have
                # any names in them from objects we've traversed thus
                # far.
                del request._steps[:]
                # gate; we don't want to do this again
                self.vroot_stack = None

        return ob2

    def before_invoke(self, published):
        request = self.request
        parents = request['PARENTS']
        # We use request.PARENTS in favor of the passed-in "published"
        # object to account for the fact that before_traverse code and
        # our next_name method mutates the parents list to insert the
        # published object
        published = parents.pop()

        # NB: it's important to reverse the parents list, or legacy VHM
        # hosting doesn't work (for one thing)
        parents.reverse()

        if hasattr(published, '__call__'):
            request.roles = getRoles(published, '__call__',
                                     published.__call__, request.roles)

        if self.browser_default and self.browser_default_redirects:
            url = request['URL']
            if not url.endswith('/'):
                # redirect
                raise httpexceptions.HTTPFound(url + '/')

        # NB: this needs to be set before we do user checking because
        # the standard acl_user's validate method relies on finding
        # request['PUBLISHED'].
        request['PUBLISHED'] = published

        user = self._get_user()
        if user is None:
            if request.roles != UNSPECIFIED_ROLES:
                self.request.response.unauthorized()
        else:
            # newSecurityManager use to be called via zpublisher_validated_hook
            newSecurityManager(request, user)
            request['AUTHENTICATED_USER'] = user

        # Run post traversal hooks
        if getattr(request, '_post_traverse', None):
            result = exec_callables(request._post_traverse)
            if result is not None:
                published = request['PUBLISHED'] = result
            del request._post_traverse # can't do post-traversal after this

        return published

    def invoke(self, published):
        # we ignore the published that gets passed in; we've set the
        # actual published object in the request within before_invoke
        request = self.request
        published = request['PUBLISHED']
        result =  mapply(published,
                         positional = request.args,
                         keyword = request,
                         debug = None,
                         maybe = 1,
                         missing_name = missing_name,
                         handle_class = dont_publish_class,
                         context = request,
                         bind=1)

        return result

    def map_result(self, result):
        # handle what response.setBody used to do
        request = self.request
        response = request.response

        if response.stdout.tell():
            # someone used response.write
            response.stdout.seek(0)
            result = response.stdout

        if result is response:
            result = response.body

        if isinstance(response, XMLRPCResponse):
            if not isinstance(result, xmlrpclib.Fault):
                result = (result,)
            result = xmlrpclib.dumps(result, methodresponse=True,
                                     allow_none=True)
            response.setHeader('content-type', 'text/xml')

        if result is None:
            result = ''
        if isinstance(result, bool):
            result = str(result)
        if isinstance(result, unicode):
            result = result.encode(self.encoding)

        if isinstance(result, basestring):
            # we can only do this set of things if the result is a string
            if not response.headers.has_key('content-type'):
                if response.isHTML(result):
                    ct = 'text/html; charset=%s' % self.encoding
                else:
                    ct = 'text/plain; charset=%s' % self.encoding
                response.setHeader('Content-Type', ct)

            # Only insert a base tag if we're serving up a browser
            # default page or a page that resulted from a method
            # default, if we're configured to not redirect browser
            # defaults, and if the content appears to be html
            default = self.browser_default or self.method_default
            if default: # XXX and (not self.browser_redirects) ?
                ct = response.headers.get('content-type', '')
                if ct.startswith('text/html'):
                    url = request['URL']
                    i = url.rfind('/')
                    if i > 0:
                        base = url[:i+1] # include the /
                        base = base.encode(self.encoding) # in case its unicode
                        result = self._insertBase(result, base)
                        response.setHeader('Content-Length', len(result))

            if not response.headers.get('content-length'):
                cl = str(len(result))
                response.setHeader('Content-Length', cl)
            result = [result]

        if not hasattr(result, '__iter__'):
            raise ValueError(
                'Unpublishable object (no __iter__ method):\n\n %s' % result)

        ct = response.headers.get('content-type', '')
        if ct.startswith('text/') and not 'charset=' in  ct:
            ct = '%s; charset=%s' % (ct, self.encoding)
            response.setHeader('content-type', ct)

        status = response.headers.get('status')
        if status is None:
            code, reason = convertResponseCode(response.status)
            status = '%d %s' % (code, reason)
        else:
            # this should not be in the headers list
            del response.headers['status']

        headers = self._getResponseHeaders()
        return status, headers, result

    def handle_exception(self, exc_info):
        t, v, tb = exc_info
        try:
            if ((t == 'Unauthorized') or
                (inspect.isclass(t) and issubclass(t, _UNAUTH_CLASSES))):
                response = self.request.response
                response._unauthorized()
                response.setStatus(401)
                val = str(v)
                return self.map_result(val)
            elif ((t == 'Redirect') or
                (inspect.isclass(t) and issubclass(t, Redirect))):
                raise httpexceptions.HTTPFound(headers=[('Location', str(v))])
            else:
                
                # we can only do this on ZODB 3.8+, otherwise we wan't doom the transaction
                if hasattr(transaction, 'doom'):
                    exc_view = queryMultiAdapter((v, self.request), name='index.html', default=None)
                    if exc_view is not None:
                        result = exc_view()
                        transaction.doom()
                        return self.map_result(result)
                
                raise t, v, tb

        finally:
            del tb # no memory leak

    # helper methods

    def _getResponseHeaders(self):
        response = self.request.response
        cookie_list = []
        for name, attrs in response.cookies.items():
            cookie = '%s="%s"' % (name, attrs['value'])
            for name, v in attrs.items():
                name = name.lower()
                if name == 'expires':
                    cookie = '%s; Expires=%s' % (cookie,v)
                elif name == 'domain':
                    cookie = '%s; Domain=%s' % (cookie,v)
                elif name == 'path':
                    cookie = '%s; Path=%s' % (cookie,v)
                elif name == 'max_age':
                    cookie = '%s; Max-Age=%s' % (cookie,v)
                elif name == 'comment':
                    cookie = '%s; Comment=%s' % (cookie,v)
                elif name == 'secure' and v:
                    cookie = '%s; Secure' % cookie
            cookie_list.append(cookie)

        cookies = [ ('set-cookie', cookie) for cookie in cookie_list ]
        cookies.sort()
        headers = response.headers.items()
        headers.sort()
        accumulated_headers = self._getAccumulatedHeaders()
        headers = headers + cookies + accumulated_headers
        httpheaders.normalize_headers(headers, strict=False)
        return headers

    def _getAccumulatedHeaders(self):
        accumulated_headers = self.request.response.accumulated_headers
        L = []
        more_headers = accumulated_headers.split('\n')
        for line in more_headers:
            if ':' in line:
                name, value = [ x.strip() for x in line.split(':', 1) ]
                L.append((name, value))
        return L

    def _get_user(self):
        user = None
        request = self.request

        for path, user_folder in self.user_folders:
            auth = request._auth
            if request.roles is UNSPECIFIED_ROLES:
                user = user_folder.validate(request, auth)
            else:
                user = user_folder.validate(request, auth, request.roles)
            if user is not None:
                request['AUTHENTICATION_PATH'] = path
                break
        return user

    def _getPublishTraverseView(self, iface, ob):
        request = self.request
        if _BETTER_THAN_210 and iface.providedBy(ob):
            adapter = ob
        else:
            adapter = queryMultiAdapter((ob, request), iface)
            if adapter is None:
                ## Zope2 doesn't set up its own adapters in a lot of cases
                ## so we will just use a default adapter.
                adapter = DefaultPublishTraverse(ob, request)

        return adapter

    def _insertBase(self, body, base):
        if body:
            match = start_of_header_search(body)
            if match is not None:
                index = match.start(0) + len(match.group(0))
                ibase = base_re_search(body)
                if ibase is None:
                    body = ('%s\n<base href="%s" />\n%s' %
                            (body[:index], escape(base, 1), body[index:]))
                    
        return body

    def _userFolderInsert(self, ob):
        user_folder = getattr(ob, '__allow_groups__', None)
        if user_folder is not None:
            path = '/'.join([''] + self.traversed)
            self.user_folders.insert(0, (path, user_folder))
    
    def _getActualURL(self, request):
        path = request.get('PATH_INFO', '')
        virtual_url = request.get('VIRTUAL_URL', '')
        
        if not virtual_url:
            return request['URL'] + quote(path)
        
        if path.endswith('/') and not virtual_url.endswith('/'):
            return virtual_url + '/'
        else:
            return virtual_url
    
    def _getPathTranslated(self, request):
        path = request.get('PATH_INFO')
        if path.endswith('/'):
            return path[:-1]
        return path
    
    def _setVirtualRoot(self, environ, path):
        from repoze.vhm.utils import getVirtualRoot
        vroot = getVirtualRoot(self.environ)
        # vroot will be the value of 'repoze.vhm.virtual_root' in the
        # environment
        if vroot:
            split_vroot = cleanPath(vroot)
            if split_vroot:
                # The vroot isn't the real root.

                # Munge the vroot path names
                vroot_path = [ '_rvh:%s' % name for name in split_vroot ]
                vroot_path = '/'.join(vroot_path)
                # Names prefixed with '_rvh:' will be popped off the
                # both the traversal request name stack and the
                # self.vroot stack within next_name() (which unmunges
                # the '_rvh:' names); we do this because the trns can
                # be mutated arbitrarily by app code and we can't just
                # count the number of pops to figure out when we've
                # popped the virtual root in order to detect when
                # we're allowed to set VirtualRootPhysicalPath at the
                # ass end of traverse().
                if not path.startswith('/'):
                    path = '/' + path
                
                # path will now contain the vroot steps instead of the
                # original path object
                
                if path.startswith(vroot):
                    path = vroot_path + path[len(vroot):]
                else:
                    path = vroot_path + path
                
                self.vroot_stack = split_vroot
                # We reverse this simply because trns is also reversed
                # (presumably so lazy people wouldn't have to type
                # pop(0); might as well ape the pattern)
                self.vroot_stack.reverse()
        return path
    
    def _hasDefaultPage(self, published, name):
        # getattr is usually used
        if getattr(published, name, None) not in _FALSETYPES:
            return True
        # Zope 2.9's Five uses adapter lookup to find the default page
        # ( see Products/Five/traversable.py(147)traverse() ).  In
        # 2.10+, getattr takes over for that purpose, so this won't
        # ever be called if the above if statement is true under 2.10+.
        lookup = (published, self.request)
        if queryMultiAdapter(lookup, Interface, name) is not None:
            return True
        return False

lock = threading.Lock()
db = None

def initialize(**config):
    global db
    if db is None:
        lock.acquire()
        try:
            db = getDB(config)
        finally:
            lock.release()
    # XXX hack for disable_gc: should be at higher level
    if asbool(config.get('disable_gc', False)):
        import gc
        gc.disable()

def get_root(helper):
    if db is None:
        raise ValueError('not initialized')

    request = helper.request

    # elide what ZApplication.ZApplicationWrapper used to do (close
    # the conn when the txn ends if the repoze.tm transaction manager
    # is in the middleware pipeline)
    conn = db.open()
    helper.conn = conn
    environ = request.environ
    t = transaction.get()
    if tm.isActive(environ):
        after_end.register(conn.close, t) 

    # get the root object
    conn.setDebugInfo(environ, request.other)
    root = conn.root()[helper.appname]

    # Elide ZPublisher.Publish and ZPublisher.BaseRequest.traverse
    root = root.__of__(RequestContainer(REQUEST=request))
    helper.root = root

    return root

