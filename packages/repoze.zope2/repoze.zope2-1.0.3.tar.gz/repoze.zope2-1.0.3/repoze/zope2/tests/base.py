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

from StringIO import StringIO

_BETTER_THAN_210 = True

try:
    # Zope 2.10+
    from zope.traversing.interfaces import TraversalError
except ImportError:
    # 2.9
    from zope.app.traversing.interfaces import TraversalError
    _BETTER_THAN_210 = False

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.interface import implements

class DummyResponse:
    unauth_called = False
    under_unauth_called = False
    urls_reset = False
    unauthorized_raises = None
    status = 200
    accumulated_headers = ''
    def __init__(self):
        self.headers = {}
        self.cookies = {}
        self.ishtml = False
        self.stdout = StringIO()
        
    def setCookie(self, name, value, **kw):
        name = str(name)
        value = str(value)

        cookies = self.cookies
        if cookies.has_key(name):
            cookie = cookies[name]
        else:
            cookie = cookies[name] = {}
        for k, v in kw.items():
            cookie[k] = v
        cookie['value'] = value
    def expireCookie(self, name, **kw):
        name = str(name)
        d = kw.copy()
        d['max_age'] = 0
        d['expires'] = 'Wed, 31-Dec-97 23:59:59 GMT'
        self.setCookie(name, 'deleted', **d)

    def getHeader(self, header):
        return self.headers.get(header)
    def setHeader(self, header, value):
        self.headers[header] = value
    def _unauthorized(self):
        self.under_unauth_called = True
    def unauthorized(self):
        self.unauth_called = True
        if self.unauthorized_raises:
            raise self.unauthorized_raises
    def isHTML(self, s):
        return self.ishtml
    def setStatus(self, v):
        self.setHeader('status', v)
        self.status = v
    def write(self, data):
        self._wrote = True
        self.stdout.write(data)


class DummyRequest:
    no_acquire_flag = False
    implements(IBrowserRequest)
    def __init__(self, env):
        self.environ = env
        if not 'TraversalRequestNameStack' in self.environ:
            self.environ['TraversalRequestNameStack'] = []
        self.response = self.RESPONSE = DummyResponse()
        self.steps = self._steps = []
        self.args = []
        from ZPublisher.BaseRequest import UNSPECIFIED_ROLES
        self.roles = UNSPECIFIED_ROLES
        self.maybe_webdav_client = False
        self.other = {}
        self._auth = ''
        self.closed = False

    def get(self, name, default):
        return self.environ.get(name, default)

    def __getitem__(self, name):
        return self.environ[name]

    def __setitem__(self, name, value):
        self.environ[name] = value

    def _resetURLS(self):
        self.urls_reset = True

    def close(self):
        self.closed = True
        
class DummyHelper:
    def __init__(self):
        self.db = None
        self.request = DummyRequest({})
        self.appname = 'Application'
        
    def get_db(self):
        self.db = DummyDB()
        return self.db
    
class DummyPublishedObject:
    result = 'published'
    exception = None
    def __init__(self):
        self.subs = {}

    def __call__(self, request=None):
        self.request = request
        if self.exception:
            raise self.exception
        return self.result

    def getPhysicalPath(self):
        return ('', 'foo')

class DummyPublishedObjectWithRoles(DummyPublishedObject):
    __roles__ = ('Manager',)

class DummyPublishedObjectWithCallRoles(DummyPublishedObject):
    __call____roles__ = ('Manager',)

class DummyGetitemPublishedObject(DummyPublishedObject):
    def __getitem__(self, name):
        return self.subs[name]

class DummyBoboTraversePublishedObject(DummyPublishedObject):
    def __bobo_traverse__(self, request, name):
        return self.subs[name]

class DummyGetattrPublishedObject(DummyPublishedObject):
    def __getattr__(self, name):
        return self.subs[name]

class DummyGetattrRaisesPublishedObject(DummyPublishedObject):
    def __getattr__(self, name):
        raise AttributeError, name

class DummyBrowserDefaultPublishedObject(DummyPublishedObject):
    bd_path = ()
    def __browser_default__(self, request):
        return self.browserdefault, self.bd_path

class DummyApplication:
    def __init__(self, conn):
        self.conn = conn

    def __of__(self, other):
        return other

class DummyConnection:
    closed = False
    debuginfo = None
    def __init__(self, db):
        self.db = db
        self.rootob = {'Application':DummyApplication(self)}

    def close(self):
        self.closed = True

    def setDebugInfo(self, info, other):
        self.debuginfo = (info, other)

    def root(self):
        return self.rootob
        
class DummyDB:
    def __init__(self):
        self.conn = DummyConnection(self)

    def open(self):
        return self.conn

class DummyTransaction:
    committed = False
    def commit(self):
        self.committed = True

def _makeEnviron():
    from StringIO import StringIO
    stdin = StringIO()
    environ = {}

    # standard CGI/WSGI things
    environ['wsgi.input'] = stdin
    environ['SERVER_NAME'] = 'localhost'
    environ['SERVER_PORT'] = '8080'
    environ['PATH_INFO'] = '/foo'

    # emulate Zope request
    environ['REQUEST_METHOD'] = 'GET'
    environ['URL'] = 'http://localhost:8080'
    environ['PARENTS'] = []
    return environ

class DummyUser:
    pass

class DummyPermissiveUserFolder:
    user = DummyUser()
    def validate(self, request, auth, roles=None):
        return self.user

class DummyNoPermissionsUserFolder:
    def validate(self, request, auth, roles=None):
        return None

