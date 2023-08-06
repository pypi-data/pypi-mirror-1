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

import sys
import unittest
from paste import httpexceptions

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.interface import directlyProvides

from repoze.zope2.tests.base import DummyHelper
from repoze.zope2.tests.base import DummyConnection
from repoze.zope2.tests.base import _makeEnviron
from repoze.zope2.tests.base import DummyRequest
from repoze.zope2.tests.base import DummyDB
from repoze.zope2.tests.base import DummyPublishedObject
from repoze.zope2.tests.base import DummyGetitemPublishedObject
from repoze.zope2.tests.base import DummyBrowserDefaultPublishedObject
from repoze.zope2.tests.base import DummyPublishedObjectWithCallRoles
from repoze.zope2.tests.base import DummyPermissiveUserFolder
from repoze.zope2.tests.base import DummyNoPermissionsUserFolder
from repoze.zope2.tests.base import DummyUser
from repoze.zope2.tests.base import _BETTER_THAN_210

class TestTopLevelFuncs(unittest.TestCase):
    def test_get_root_initialized(self):
        from repoze.zope2.z2bob import get_root
        from repoze.zope2 import z2bob
        z2bob.db = DummyDB()
        try:
            helper = DummyHelper()
            root = get_root(helper)
            from ZPublisher.BaseRequest import RequestContainer
            self.failUnless(isinstance(root, RequestContainer), root)
        finally:
            z2bob.db = None

    def test_get_root_not_initialized(self):
        from repoze.zope2.z2bob import get_root
        helper = DummyHelper()
        self.assertRaises(ValueError, get_root, helper)

    def test_get_root_with_tm_in_pipeline(self):
        from repoze.zope2.z2bob import get_root
        from repoze.zope2 import z2bob
        z2bob.db = DummyDB()
        try:
            helper = DummyHelper()
            helper.request.environ['repoze.tm.active'] = True
            root = get_root(helper)
            import transaction
            t = transaction.get()
            from repoze.tm import after_end
            self.assertEqual(len(getattr(t, after_end.key)), 1)
            delattr(t, after_end.key)
        finally:
            z2bob.db = None

    def test_quote(self):
        from repoze.zope2.z2bob import quote
        quoted = quote('http://foo/bar/@@view')
        self.assertEqual(quoted, 'http%3A//foo/bar/@@view')

    def test_cleanPath_bad_name(self):
        from repoze.zope2.z2bob import cleanPath
        from paste.httpexceptions import HTTPForbidden
        self.assertRaises(HTTPForbidden, cleanPath, '/foo/REQUEST')
        self.assertRaises(HTTPForbidden, cleanPath, '/foo/aq_self')
        self.assertRaises(HTTPForbidden, cleanPath, '/foo/aq_base')
        
    def test_cleanPath_path_startswith_endswith(self):
        from repoze.zope2.z2bob import cleanPath
        self.assertEqual(cleanPath('/foo/'), ['foo'])

    def test_cleanPath_empty_elements(self):
        from repoze.zope2.z2bob import cleanPath
        self.assertEqual(cleanPath('foo///'), ['foo'])

    def test_cleanPath_onedot(self):
        from repoze.zope2.z2bob import cleanPath
        self.assertEqual(cleanPath('foo/./bar'), ['foo', 'bar'])

    def test_cleanPath_twodots(self):
        from repoze.zope2.z2bob import cleanPath
        self.assertEqual(cleanPath('foo/../bar'), ['bar'])

    def test_initialize_gcdisable(self):
        from repoze.zope2 import z2bob
        reenable = False
        import gc
        if gc.isenabled():
            reenable = True
        try:
            old = z2bob.db
            z2bob.db = True
            z2bob.initialize(disable_gc='true')
            self.failIf(gc.isenabled())
        finally:
            z2bob.db = old
            if reenable:
                gc.enable()

class TestZope2ObobHelper(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        from zope.security.management import endInteraction
        from zope.security.management import queryInteraction
        if queryInteraction() is not None:
            endInteraction()
        from AccessControl.SecurityManagement import noSecurityManager
        noSecurityManager()
        PlacelessSetup.tearDown(self)
        
    def _getTargetClass(self):
        from repoze.zope2.z2bob import Zope2ObobHelper
        return Zope2ObobHelper

    def _makeOne(self, env=None, **config2):
        if env is None:
            env = _makeEnviron()
        config = {'zope.conf':None, 'encoding':'utf-8'}
        config.update(config2)
        helper = self._getTargetClass()(env, **config)
        helper.request = DummyRequest(env)
        return helper

    def test_ctor(self):
        environ = {}
        helper = self._makeOne(environ)
        self.assertEqual(helper.environ, environ)
        self.assertEqual(helper.encoding, 'utf-8')
        self.assertEqual(helper.appname, 'Application')
        self.assertEqual(helper.browser_default_redirects, False)

    def test_ctor_nondefaults(self):
        environ = {}
        helper = self._makeOne(environ, appname='Application2',
                               browser_default_redirects='true',
                               disable_gc='true')
        self.assertEqual(helper.appname, 'Application2')
        self.assertEqual(helper.browser_default_redirects, True)

    def test_setup(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(env['SERVER_URL'], 'http://www.example.com')
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        self.failUnless(IDefaultBrowserLayer.providedBy(helper.request))
        self.assertNotEqual(queryInteraction(), None)
        self.assertEqual(helper.request['URL'], 'http://www.example.com')
        self.assertEqual(helper.request['ACTUAL_URL'], 'http://www.example.com/foo/space%20in%20name')
        self.assertEqual(helper.default_page, 'index_html')
        self.assertEqual(helper.vroot_stack, None)
        self.assertEqual(helper.clean, ['foo', 'space in name'])
        self.assertEqual(helper.request.path, ['space in name', 'foo'])
    
    def test_setup_path_translated_trailing(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name/'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEquals(helper.request['PATH_TRANSLATED'], '/foo/space in name')
    
    def test_setup_path_translated_no_trailing(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEquals(helper.request['PATH_TRANSLATED'], '/foo/space in name')
    
    def test_setup_no_virtual_url(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.failIf('VIRTUAL_URL' in helper.request)
        self.failIf('VIRTUAL_URL_PARTS' in helper.request)
        self.assertEqual(helper.request['ACTUAL_URL'], 'http://www.example.com/foo/space%20in%20name')
    
    def test_setup_virtual_url_no_slash(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name'
        env['repoze.vhm.virtual_url'] = 'http://www.example.com/space in name'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(helper.request['VIRTUAL_URL'], 'http://www.example.com/space%20in%20name')
        self.assertEqual(helper.request['VIRTUAL_URL_PARTS'], ['http://www.example.com', 'space%20in%20name'])
        self.assertEqual(helper.request['ACTUAL_URL'], 'http://www.example.com/space%20in%20name')
    
    def test_setup_virtual_url_with_slash(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name/'
        env['repoze.vhm.virtual_url'] = 'http://www.example.com/space in name'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(helper.request['VIRTUAL_URL'], 'http://www.example.com/space%20in%20name')
        self.assertEqual(helper.request['VIRTUAL_URL_PARTS'], ['http://www.example.com', 'space%20in%20name'])
        self.assertEqual(helper.request['ACTUAL_URL'], 'http://www.example.com/space%20in%20name/')

    def test_url_quoting(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/foo/space in name/'
        env['repoze.vhm.virtual_url'] = 'http://www.example.com/space in name'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()

        class PublishableDummy(DummyGetitemPublishedObject):
            """Duh
            """
        
        root = PublishableDummy()
        root.subs['foo'] = PublishableDummy()
        root.subs['foo'].subs['space in name'] = PublishableDummy()
        
        current = root
        
        helper.before_traverse(current)
        name = helper.next_name()
        current = helper.traverse(current, name)
        
        helper.before_traverse(current)
        name = helper.next_name()
        current = helper.traverse(current, name)
        
        self.assertEqual(helper.request['PATH_INFO'], '/foo/space in name/')
        self.assertEqual(helper.request['PATH_TRANSLATED'], '/foo/space in name')
        self.assertEqual(helper.request['URL'], 'http://www.example.com/foo/space%20in%20name')
        self.assertEqual(helper.request['VIRTUAL_URL'], 'http://www.example.com/space%20in%20name')
        self.assertEqual(helper.request['ACTUAL_URL'], 'http://www.example.com/space%20in%20name/')
    
    def test_setup_xmlrpcresponse(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['CONTENT_TYPE'] = 'text/xml'
        env['REQUEST_METHOD'] = 'POST'
        import StringIO
        s = """<?xml version="1.0"?>
        <methodCall>
        <methodName>examples.getStateName</methodName>
        <params>
        <param>
        <value><i4>41</i4></value>
        </param>
        </params>
        </methodCall>
        """
        env['wsgi.input'] = StringIO.StringIO(s)
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(helper.default_page, 'POST')

    def test_setup_probablydav(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['REQUEST_METHOD'] = 'PUT'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(helper.default_page, 'PUT')
        self.assertEqual(helper.request.no_acquire_flag, True)

    def test_setup_with_vroot(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['repoze.vhm.virtual_url'] = 'http://www.example.com/foo'
        env['repoze.vhm.virtual_root'] = '/cms'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(env['SERVER_URL'], 'http://www.example.com')
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        self.failUnless(IDefaultBrowserLayer.providedBy(helper.request))
        self.assertNotEqual(queryInteraction(), None)
        self.assertEqual(helper.request['URL'], 'http://www.example.com')
        self.assertEqual(helper.request['ACTUAL_URL'],
                         'http://www.example.com/foo')
        self.assertEqual(helper.default_page, 'index_html')
        self.assertEqual(helper.vroot_stack, ['cms'])
        self.assertEqual(helper.request['TraversalRequestNameStack'],
                         ['foo', '_rvh:cms'])
    
    def test_setup_with_vroot_and_path(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['PATH_INFO'] = '/cms/foo'
        env['repoze.vhm.virtual_url'] = 'http://www.example.com/foo'
        env['repoze.vhm.virtual_root'] = '/cms'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(env['SERVER_URL'], 'http://www.example.com')
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        self.failUnless(IDefaultBrowserLayer.providedBy(helper.request))
        self.assertNotEqual(queryInteraction(), None)
        self.assertEqual(helper.request['URL'], 'http://www.example.com')
        self.assertEqual(helper.request['ACTUAL_URL'], 'http://www.example.com/foo')
        self.assertEqual(helper.default_page, 'index_html')
        self.assertEqual(helper.vroot_stack, ['cms'])
        self.assertEqual(helper.request['TraversalRequestNameStack'],
                         ['foo', '_rvh:cms'])

    def test_setup_with_empty_vroot(self):
        from zope.security.management import queryInteraction
        from zope.security.management import endInteraction
        env = _makeEnviron()
        env['SERVER_NAME'] = 'www.example.com'
        env['SERVER_PORT'] = '80'
        env['repoze.vhm.virtual_root'] = '//'
        helper = self._makeOne(env)
        if queryInteraction() is not None:
            endInteraction()
        helper.setup()
        self.assertEqual(env['SERVER_URL'], 'http://www.example.com')
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        self.failUnless(IDefaultBrowserLayer.providedBy(helper.request))
        self.assertNotEqual(queryInteraction(), None)
        self.assertEqual(helper.vroot_stack, None)
        self.assertEqual(helper.request['TraversalRequestNameStack'],
                         ['foo'])

    def test_teardown(self):
        from zope.security.management import queryInteraction
        from zope.security.management import newInteraction
        from zope.security.management import endInteraction
        from AccessControl.SecurityManagement import newSecurityManager
        from AccessControl.SecurityManagement import _managers
        helper = self._makeOne()
        if queryInteraction() is not None:
            endInteraction()
        newInteraction()
        interaction = queryInteraction()
        newSecurityManager(None, DummyUser())
        request = helper.request
        helper.teardown()
        self.assertEqual(queryInteraction(), None)
        self.assertEqual(request.closed, True)
        self.assertEqual(_managers,{}) # noSecurityManager called
        self.assertEqual(request.response, None) # explicitly cleared
        self.assertEqual(helper.request, None)
        self.assertEqual(helper.user_folders, None)
        self.assertEqual(helper.vroot_stack, None)
        self.assertEqual(helper.root, None)
        self.assertEqual(helper.browser_default_published, None)

    def test_next_name(self):
        helper = self._makeOne()
        helper.request['TraversalRequestNameStack'] = ['bar', 'foo']
        helper.request['PARENTS'].append(None)
        self.assertEqual(helper.next_name(), 'foo')
        self.assertEqual(helper.next_name(), 'bar')
        self.assertEqual(helper.next_name(), None)

    def test_next_name_trns_empty_no_browserdefault_default_page_exists(self):
        published = DummyPublishedObject()
        published.index_html = lambda * x: 'hello!'
        helper = self._makeOne()
        helper.request['URL'] = 'http://www.example.com'
        parents = helper.request['PARENTS']
        parents.append(published)
        result = helper.next_name()
        self.assertEqual(helper.browser_default, False)
        self.assertEqual(helper.browser_default_published, None)
        self.assertEqual(result, 'index_html')

    def test_next_name_trns_empty_no_browserdefault_default_page_missing(self):
        published = DummyPublishedObject()
        published.index_html = None
        helper = self._makeOne()
        helper.request['URL'] = 'http://www.example.com'
        parents = helper.request['PARENTS']
        parents.append(published)
        result = helper.next_name()
        self.assertEqual(helper.browser_default, False)
        self.assertEqual(helper.browser_default_published, None)
        self.assertEqual(result, None)

    def test_next_name_trns_empty_browserdefault_returns_new_published(self):
        published = DummyBrowserDefaultPublishedObject()
        browserdefault = DummyPublishedObject()
        published.browserdefault = browserdefault
        published.bd_path = ()
        browserdefault.index_html = lambda * x: 'hello!'
        helper = self._makeOne()
        parents = helper.request['PARENTS']
        parents.append(published)
        result = helper.next_name()
        self.assertEqual(helper.browser_default, True)
        self.assertEqual(helper.browser_default_published, browserdefault)
        self.assertEqual(result, 'index_html')

    def test_next_name_trns_empty_browserdefault_returns_path_len_1(self):
        published = DummyBrowserDefaultPublishedObject()
        published.browserdefault = published
        published.bd_path = ('nondefault',)
        published.nondefault = lambda * x: 'hello!'
        helper = self._makeOne()
        parents = helper.request['PARENTS']
        parents.append(published)
        result = helper.next_name()
        self.assertEqual(helper.browser_default, True)
        self.assertEqual(helper.browser_default_published, None)
        self.assertEqual(result, 'nondefault')

    def test_next_name_trns_empty_browserdefault_returns_path_len_2(self):
        published = DummyBrowserDefaultPublishedObject()
        published.browserdefault = published
        published.bd_path = ('foo', 'nondefault',)
        published.nondefault = lambda * x: 'hello!'
        helper = self._makeOne()
        parents = helper.request['PARENTS']
        parents.append(published)
        result = helper.next_name()
        self.assertEqual(helper.browser_default, True)
        self.assertEqual(helper.browser_default_published, None)
        self.assertEqual(result, 'nondefault')

    def test_next_name_trns_empty_browserdefault_returns_path_to_view(self):
        published = DummyBrowserDefaultPublishedObject()
        published.browserdefault = published
        published.bd_path = ('nondefault',)
        class DummyView:
            def __init__(self, context, request):
                pass
        from zope.publisher.interfaces.browser import IBrowserRequest
        from zope.interface import Interface
        if _BETTER_THAN_210:
            ztapi.provideAdapter((Interface, IBrowserRequest), Interface,
                                 DummyView, 'nondefault')
        else:
            ztapi.provideView(None, IBrowserRequest, Interface,
                              'nondefault', DummyView)
        helper = self._makeOne()
        parents = helper.request['PARENTS']
        parents.append(published)
        result = helper.next_name()
        self.assertEqual(helper.browser_default, True)
        self.assertEqual(helper.browser_default_published, None)
        self.assertEqual(result, 'nondefault')

    def test_next_name_with_rvh_novhost(self):
        helper = self._makeOne()
        helper.request['TraversalRequestNameStack'] = ['bar', '_rvh:foo']
        helper.request['PARENTS'].append(None)
        helper.vroot_stack = None
        self.assertEqual(helper.next_name(), '_rvh:foo')
        self.assertEqual(helper.next_name(), 'bar')
        self.assertEqual(helper.next_name(), None)

    def test_next_name_with_rvh_vhost(self):
        helper = self._makeOne()
        helper.request['TraversalRequestNameStack'] = ['bar', '_rvh:foo']
        helper.request['PARENTS'].append(None)
        helper.vroot_stack = ['_rvh:foo']
        self.assertEqual(helper.next_name(), 'foo')
        self.assertEqual(helper.vroot_stack, [])
        self.assertEqual(helper.next_name(), 'bar')
        self.assertEqual(helper.next_name(), None)

    def test_before_traverse_calls_bpth(self):
        published = DummyPublishedObject()
        L = []
        published.__before_publishing_traverse__ = lambda *arg: L.append(arg)
        helper = self._makeOne()
        helper.before_traverse(published)
        self.assertEqual(L, [(published, helper.request)])

    def test_before_traverse_inserts_parent(self):
        published = DummyPublishedObject()
        helper = self._makeOne()
        helper.request['PARENTS'].append(published)
        helper.before_traverse(published)
        self.assertEqual(helper.request['PARENTS'][0], published)

    def test_traverse_munges_url_before_calling_publishttraverse(self):
        published = DummyGetitemPublishedObject()
        helper = self._makeOne()
        helper.request['URL'] = 'http://www.example.com'
        self.assertRaises(httpexceptions.HTTPNotFound,
                          helper.traverse, published, '@@notthere')

        # Ensure that the URL had the name added to it *before*
        # publishtraverse blew up; this is required by the ZMI:
        # App.FactoryDispatcher.FactoryDispatcher *caches* part of the
        # URL (stupidly) during its traversal, to be used later, so
        # the URL needs to be as-fully-constructed as possible before
        # an object's traversal method is called, even though it
        # really shouldn't matter (things that are called during
        # traversal which depends on request['URL'] are insane,
        # because it's computed *during* traversal, and things that
        # cache the value instead of recomputing it later as necessary
        # deserve to lose, but c'est la vie).

        self.assertEqual(helper.request['URL'],
                         'http://www.example.com/@@notthere')

    def test_traverse_inserts_user_folder(self):
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        helper.traverse(published, 'foo')
        self.assertEqual(helper.user_folders,
                         [('', published.__allow_groups__)])

    def test_traverse_with_empty_vroot_stack(self):
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        env = _makeEnviron()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        helper.request._steps = ['bar']
        helper.vroot_stack = []
        helper.traverse(published, 'foo')
        self.assertEqual(helper.request.other['VirtualRootPhysicalPath'],
                         ('', 'foo'))
        self.assertEqual(helper.request._steps, [])
        self.assertEqual(helper.vroot_stack, None)

    def test_traverse_with_nonempty_vroot_stack(self):
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        env = _makeEnviron()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        helper.request._steps = ['bar']
        helper.vroot_stack = ['buz']
        helper.traverse(published, 'foo')
        request = helper.request
        self.assertEqual(request.other.get('VirtualRootPhysicalPath'), None)
        self.assertEqual(helper.request._steps, ['bar'])
        self.assertEqual(helper.vroot_stack, ['buz'])

    def test_traverse_nslookup_to_bad_viewname_raises_HTTPNotFound(self):
        published = DummyPublishedObject()
        helper = self._makeOne()
        self.assertRaises(httpexceptions.HTTPNotFound, helper.traverse,
                          published, '@@notthere')

    def test_traverse_nslookup_no_traversal_error(self):
        # CM: If you see me on TV in an orange jumpsuit and shackles,
        # don't judge me, it's only because this test took two hours
        # to write.
        published = DummyPublishedObject()
        helper = self._makeOne()
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        directlyProvides(helper.request, IDefaultBrowserLayer)
        class OfObj:
            def __of__(self, other):
                other.ofed = True
                return other
        class View:
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def traverse(self, name, remaining):
                return OfObj()
        try:
            from zope.traversing.interfaces import ITraversable
        except ImportError:
            from zope.app.traversing.interfaces import ITraversable
        ztapi.browserView(None, 'view', View, providing=ITraversable)
        result = helper.traverse(published, '@@thistestiswaywaytoohardtowrite')
        self.assertEqual(result, published)
        self.assertEqual(published.ofed, True)

    def test_traverse_nslookup_no_traversal_error_bd_published(self):
        published = DummyPublishedObject()
        browserdefault = DummyPublishedObject()
        helper = self._makeOne()
        helper.browser_default_published = browserdefault
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        directlyProvides(helper.request, IDefaultBrowserLayer)
        class OfObj:
            def __of__(self, other):
                other.ofed = True
                return other
        class View:
            def __init__(self, context, request):
                self.context = context
                self.request = request
            def traverse(self, name, remaining):
                return OfObj()
        try:
            from zope.traversing.interfaces import ITraversable
        except ImportError:
            from zope.app.traversing.interfaces import ITraversable
        ztapi.browserView(None, 'view', View, providing=ITraversable)
        result = helper.traverse(published, '@@thistestiswaywaytoohardtowrite')
        self.assertEqual(result, browserdefault)
        self.assertEqual(browserdefault.ofed, True)

    def test_traverse_sets_request_roles(self):
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        foo.__doc__ = 'hello'
        foo.__roles__ = ('a', 'b', 'c')
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        helper.traverse(published, 'foo')
        self.assertEqual(helper.request.roles, ('a', 'b', 'c'))

    def test_traverse_traversed_fixed(self):
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        helper.traverse(published, 'foo')
        self.assertEqual(helper.traversed, ['foo'])

    def test_traverse_urls_reset(self):
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        x = []
        helper.request._resetURLS = lambda *arg: x.append(1)
        helper.traverse(published, 'foo')
        self.assertEqual(x, [1])

    if _BETTER_THAN_210:
        # I can't make ztapi.browserViewProviding register the correct
        # stuff under 2.9 (CM)
        def test_traverse_ob_has_IPublishTraverse_multiadapter(self):
            from zope.publisher.interfaces import IPublishTraverse
            from zope.interface import implements
            x = []
            class DummyPublishTraverse:
                implements(IPublishTraverse)
                def __init__(self, context, request):
                    pass
                def publishTraverse(self, request, name):
                    x.append(request)
                    x.append(name)
            published = DummyGetitemPublishedObject()
            ztapi.browserViewProviding(None, DummyPublishTraverse,
                                       layer=None,
                                       providing=IPublishTraverse)
            foo = DummyPublishedObject()
            foo.__doc__ = 'hello'
            published.subs['foo'] = foo
            published.__allow_groups__ = object()
            helper = self._makeOne()
            helper.user_folders = []
            helper.request.steps = []
            x = []
            helper.traverse(published, 'foo')
            self.assertEqual(len(x), 2)
            self.assertEqual(x[0], helper.request)
            self.assertEqual(x[1], 'foo')

    def test_traverse_ob_implements_IPublishTraverser(self):
        from zope.publisher.interfaces import IPublishTraverse
        from zope.interface import directlyProvides
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        directlyProvides(published, IPublishTraverse)
        x = []
        published.publishTraverse = lambda *args: x.append(args)
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        helper.traverse(published, 'foo')
        from repoze.zope2.publishtraverse import _BETTER_THAN_210
        if _BETTER_THAN_210: # 2.10 semantics return the published ob
            self.assertEqual(len(x), 1)
            xrequest, xname = x[0]
            self.assertEqual(xrequest, helper.request)
            self.assertEqual(xname, 'foo')
        else:
            self.assertEqual(len(x), 0)
    
    def test_traverse_ob_implements_IPublishTraverser_throws_key_error_gives_404(self):
        from zope.publisher.interfaces import IPublishTraverse
        from zope.interface import directlyProvides
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        directlyProvides(published, IPublishTraverse)
        x = []
        
        def publishTraverseRaise(request, name):
            raise KeyError(name)
        
        published.publishTraverse = publishTraverseRaise
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        self.assertRaises(httpexceptions.HTTPNotFound,
                          helper.traverse, published, 'random')
    
    def test_traverse_ob_implements_IPublishTraverser_throws_attribute_error_gives_404(self):
        from zope.publisher.interfaces import IPublishTraverse
        from zope.interface import directlyProvides
        published = DummyGetitemPublishedObject()
        foo = DummyPublishedObject()
        directlyProvides(published, IPublishTraverse)
        x = []
        
        def publishTraverseRaise(request, name):
            raise AttributeError(name)
        
        published.publishTraverse = publishTraverseRaise
        foo.__doc__ = 'hello'
        published.subs['foo'] = foo
        published.__allow_groups__ = object()
        helper = self._makeOne()
        helper.user_folders = []
        helper.request.steps = []
        self.assertRaises(httpexceptions.HTTPNotFound,
                          helper.traverse, published, 'random')
        
    def test_before_invoke_browser_default_redirects(self):
        published = DummyPublishedObject()
        helper = self._makeOne(browser_default_redirects=True)
        helper.browser_default = True
        helper.request['PARENTS'].append(published)
        self.assertRaises(httpexceptions.HTTPFound,
                          helper.before_invoke, published)

    def test_before_invoke_browser_default_doesnt_redirect(self):
        published = DummyPublishedObject()
        helper = self._makeOne(browser_default_redirects=False)
        helper.request['PARENTS'].append(published)
        helper.user_folders = [] # dont do authorization
        result = helper.before_invoke(published)
        self.assertEqual(result, published)
        self.assertEqual(helper.request['PUBLISHED'], published)

    def test_before_invoke_callroles_unathorized(self):
        published = DummyPublishedObjectWithCallRoles()
        helper = self._makeOne()
        helper.request['PARENTS'].append(published)
        helper.before_invoke(published)
        self.assertEqual(helper.request.response.unauth_called, True)

    def test_before_invoke_callroles_response_unauthorized_raises_unauth(self):
        published = DummyPublishedObjectWithCallRoles()
        helper = self._makeOne()
        # zExceptions.Unauthorized
        from zExceptions import Unauthorized
        helper.request.response.unauthorized_raises = Unauthorized
        helper.request['PARENTS'].append(published)
        self.assertRaises(Unauthorized, helper.before_invoke, published)
        # AccessControl.Unauthorized
        from AccessControl import Unauthorized
        helper.request.response.unauthorized_raises = Unauthorized
        helper.request['PARENTS'].append(published)
        self.assertRaises(Unauthorized, helper.before_invoke, published)

    def test_before_invoke_callroles_authorized(self):
        published = DummyPublishedObjectWithCallRoles()
        helper = self._makeOne()
        helper.user_folders = [('', DummyPermissiveUserFolder())]
        helper.request['PARENTS'].append(published)
        result = helper.before_invoke(published)
        self.assertEqual(helper.request.response.unauth_called, False)
        self.assertEqual(helper.request['PUBLISHED'], published)
        self.assertEqual(result, published)

    def test_before_invoke_user_unauthorized(self):
        published = DummyPublishedObject()
        helper = self._makeOne()
        request = helper.request
        request.roles = ['some roles']
        helper.user_folders = [('', DummyNoPermissionsUserFolder())]
        # zExceptions.Unauthorized
        from zExceptions import Unauthorized
        request.response.unauthorized_raises = Unauthorized
        request['PARENTS'].append(published)
        self.assertRaises(Unauthorized, helper.before_invoke, published)
        # AccessControl.Unauthorized
        from AccessControl import Unauthorized
        request.response.unauthorized_raises = Unauthorized
        request['PARENTS'].append(published)
        self.assertRaises(Unauthorized, helper.before_invoke, published)

    def test_before_invoke_user_authorized(self):
        published = DummyPublishedObject()
        helper = self._makeOne()
        request = helper.request
        request.roles = ['some roles']
        uf = DummyPermissiveUserFolder()
        helper.user_folders = [('', uf)]
        # zExceptions.Unauthorized
        from zExceptions import Unauthorized
        request.response.unauthorized_raises = Unauthorized
        request['PARENTS'].append(published)
        result = helper.before_invoke(published)
        self.assertEqual(request['AUTHENTICATED_USER'], uf.user)

    def test_before_invoke_with_post_traverse(self):
        published = DummyPublishedObject()
        other = DummyPublishedObject()
        helper = self._makeOne()
        helper.request._post_traverse = [(lambda *x: other, ())]
        helper.request['PARENTS'].append(published)
        result = helper.before_invoke(published)
        self.assertEqual(result, other)
        self.assertEqual(helper.request['PUBLISHED'], other)

    def test_invoke_ignores_published_and_uses_request_published(self):
        published = DummyPublishedObject()
        helper = self._makeOne()
        helper.request['PUBLISHED'] = published
        result = helper.invoke(None)
        self.assertEqual(result, 'published')

    def test_invoke_mapply_passes_exception_up(self):
        published = DummyPublishedObject()
        from zExceptions import Redirect
        published.exception = Redirect('foo')
        helper = self._makeOne()
        helper.request['PUBLISHED'] = published
        self.assertRaises(Redirect, helper.invoke, published)

    def test_map_result_string_with_content_length(self):
        helper = self._makeOne()
        helper.request.response.headers['status'] = '200 OK'
        helper.request.response.headers['Content-Length'] = '5'
        status, headers, result = helper.map_result('a')
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['a'])
        self.assertEqual(headers[0], ('Content-Length', '1'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/plain; charset=utf-8'))

    def test_map_result_string_no_content_length(self):
        helper = self._makeOne()
        helper.request.response.headers['status'] = '200 OK'
        status, headers, result = helper.map_result('a')
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['a'])
        self.assertEqual(headers[0], ('Content-Length', '1'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/plain; charset=utf-8'))

    def test_map_result_string_has_content_type(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'image/jpg'
        status, headers, result = helper.map_result('hello')
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['hello'])
        self.assertEqual(headers[0], ('Content-Length', '5'))
        self.assertEqual(headers[1], ('Content-Type', 'image/jpg'))

    def test_map_result_None(self):
        helper = self._makeOne()
        helper.request.response.headers['status'] = '200 OK'
        status, headers, result = helper.map_result(None)
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, [''])
        self.assertEqual(headers[0], ('Content-Length', '0'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/plain; charset=utf-8'))

    def test_map_result_bool(self):
        helper = self._makeOne()
        helper.request.response.headers['status'] = '200 OK'
        status, headers, result = helper.map_result(True)
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['True'])
        self.assertEqual(headers[0], ('Content-Length', '4'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/plain; charset=utf-8'))

    def test_map_result_response(self):
        helper = self._makeOne()
        helper.request.response.headers['status'] = '200 OK'
        helper.request.response.body = 'body'
        status, headers, result = helper.map_result(helper.request.response)
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['body'])
        self.assertEqual(headers[0], ('Content-Length', '4'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/plain; charset=utf-8'))

    def test_map_result_response_written(self):
        # if response.write is used, a tempfile is used to hold
        # the result, and it becomes the body of the response
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.write('body')
        status, headers, result = helper.map_result(None)
        self.assertEqual(response._wrote, True)
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, response.stdout)
        self.assertEqual(result.read(), 'body')

    def test_map_result_headers_normalized(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['x-foobar'] = 'foobar'
        status, headers, result = helper.map_result('abc')
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['abc'])
        self.assertEqual(headers[0], ('Content-Length', '3'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/plain; charset=utf-8'))
        self.assertEqual(headers[2], ('X-Foobar', 'foobar'))

    def test_map_result_unicode_gets_encoded(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        helper.encoding = 'utf-8'
        status, headers, result = helper.map_result(u'fi\xed')
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['fi\xc3\xad'])
        self.assertEqual(headers[0], ('Content-Length', '4'))

    def test_map_result_with_iterator(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        helper.encoding = 'utf-8'
        status, headers, result = helper.map_result(['hello'])
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, ['hello'])
        self.assertEqual(headers, [])

    def test_map_result_string_no_content_type_sets_content_type_ashtml(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        body = '<html><head></head><body></body></html>'
        response.ishtml = True
        status, headers, result = helper.map_result(body)
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, [body])
        self.assertEqual(headers[0], ('Content-Length', '39'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/html; charset=utf-8'))
        
    def test_map_result_string_no_browser_default_redirect_ashtml_not_bd(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        helper.request['URL'] = 'http://www.example.com/baz/foo.html'
        body = '<html><head></head><body></body></html>'
        status, headers, result = helper.map_result(body)
        self.assertEqual(status, '200 OK')
        self.assertEqual(result, [body])
        self.assertEqual(headers[0], ('Content-Length', str(len(body))))

    def test_map_result_string_no_browser_default_redirect_ashtml_as_bd(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        helper.request['URL'] = 'http://www.example.com/baz/foo.html'
        body = '<html><head></head><body></body></html>'
        helper.browser_default = True
        status, headers, result = helper.map_result(body)
        self.assertEqual(status, '200 OK')
        base = '\n<base href="http://www.example.com/baz/" />\n'
        self.failIfEqual(result[0].find(base), -1)
        expected_len =len(body) + len(base)
        self.assertEqual(headers[0], ('Content-Length', str(expected_len)))

    def test_map_result_string_no_browser_default_redirect_nothtml_as_bd(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        helper.request['URL'] = 'http://www.example.com/baz/foo.html'
        body = 'foo'
        helper.browser_default = True
        status, headers, result = helper.map_result(body)
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers[0], ('Content-Length', str(len(body))))

    def test_map_result_string_method_default_html(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        helper.request['URL'] = 'http://www.example.com/baz/pt_editAction'
        body = '<html><head></head><body></body></html>'
        helper.method_default = True
        status, headers, result = helper.map_result(body)
        self.assertEqual(status, '200 OK')
        base = '\n<base href="http://www.example.com/baz/" />\n'
        self.failIfEqual(result[0].find(base), -1)
        expected_len =len(body) + len(base)
        self.assertEqual(headers[0], ('Content-Length', str(expected_len)))

    def test_unicode_url_is_converted_during_insert_base(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        helper.request['URL'] = u'http://www.example.com/baz/pt_editAction'
        body = '<html><head></head><body></body></html>'
        helper.method_default = True
        status, headers, result = helper.map_result(body)
        self.assertEqual(type(result[0]), str)
        base = '\n<base href="http://www.example.com/baz/" />\n'
        expected_len =len(body) + len(base)
        self.assertEqual(headers[0], ('Content-Length', str(expected_len)))

    def test_map_result_xmlrpc_request_string(self):
        from ZPublisher.xmlrpc import Response
        import xmlrpclib
        helper = self._makeOne()
        xmlrpcresponse = Response(helper.request.response)
        helper.request.response = xmlrpcresponse
        status, headers, result = helper.map_result('hello')
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers[0], ('Content-Length', '131'))
        self.assertEqual(headers[1], ('Content-Type','text/xml; charset=utf-8'))
        self.assertEqual(len(result), 1)
        body = result[0]
        v = xmlrpclib.loads(body)
        self.assertEqual(v, (('hello',), None))

    def test_map_result_xmlrpc_request_dict(self):
        from ZPublisher.xmlrpc import Response
        import xmlrpclib
        helper = self._makeOne()
        xmlrpcresponse = Response(helper.request.response)
        helper.request.response = xmlrpcresponse
        status, headers, result = helper.map_result(
            {'l1':{'l2':('a', 'b', 'c')}})
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers[0], ('Content-Length', '378'))
        self.assertEqual(headers[1], ('Content-Type','text/xml; charset=utf-8'))
        self.assertEqual(len(result), 1)
        body = result[0]
        v = xmlrpclib.loads(body)
        self.assertEqual(v, (({'l1':{'l2':['a', 'b', 'c']}},), None))

    def test_map_result_xmlrpc_request_None(self):
        from ZPublisher.xmlrpc import Response
        import xmlrpclib
        helper = self._makeOne()
        xmlrpcresponse = Response(helper.request.response)
        helper.request.response = xmlrpcresponse
        status, headers, result = helper.map_result(None)
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers[0], ('Content-Length', '114'))
        self.assertEqual(headers[1], ('Content-Type','text/xml; charset=utf-8'))
        self.assertEqual(len(result), 1)
        body = result[0]
        v = xmlrpclib.loads(body)
        self.assertEqual(v, ((None,), None))

    def test_map_result_xmlrpc_request_simple_instance(self):
        from ZPublisher.xmlrpc import Response
        import xmlrpclib
        helper = self._makeOne()
        xmlrpcresponse = Response(helper.request.response)
        helper.request.response = xmlrpcresponse
        class Foo:
            def __init__(self):
                self.a = 1
                self.b = 2
        status, headers, result = helper.map_result(Foo())
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers[0], ('Content-Length', '251'))
        self.assertEqual(headers[1], ('Content-Type','text/xml; charset=utf-8'))
        self.assertEqual(len(result), 1)
        body = result[0]
        v = xmlrpclib.loads(body)
        self.assertEqual(v, (({'a':1, 'b':2},), None))

    def test_map_result_xmlrpc_request_complex_instance(self):
        from ZPublisher.xmlrpc import Response
        helper = self._makeOne()
        from Queue import Queue
        xmlrpcresponse = Response(helper.request.response)
        helper.request.response = xmlrpcresponse
        self.assertRaises(TypeError, helper.map_result, Queue())

    def test_map_result_xmlrpc_fault(self):
        from ZPublisher.xmlrpc import Response
        import xmlrpclib
        helper = self._makeOne()
        fault = xmlrpclib.Fault(10, 'ten', foo='bar', baz='buz')
        xmlrpcresponse = Response(helper.request.response)
        helper.request.response = xmlrpcresponse
        status, headers, result = helper.map_result(fault)
        self.assertEqual(status, '200 OK')
        self.assertEqual(headers[0], ('Content-Length', '259'))
        self.assertEqual(headers[1], ('Content-Type','text/xml; charset=utf-8'))
        self.assertEqual(len(result), 1)
        body = result[0]
        self.assertRaises(xmlrpclib.Fault, xmlrpclib.loads, body)

    def test_map_result_tacks_on_charset_to_text_responses(self):
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        status, headers, result = helper.map_result('foo')
        self.assertEqual(headers[0], ('Content-Length', '3'))
        self.assertEqual(headers[1], ('Content-Type',
                                      'text/html; charset=utf-8'))

    def test_map_result_adds_cookies_to_headers(self):
        helper = self._makeOne()
        response = helper.request.response
        response.setCookie('secure', 'abc', secure=True)
        response.setCookie('domain', 'abc', domain='www.example.com')
        response.setCookie('path', 'abc', path='/foo/bar')
        response.setCookie('max_age', 'abc', max_age='1')
        response.setCookie('comment', 'abc', comment='abc')
        response.setCookie('secure', 'abc', secure=True)
        response.setCookie('multi', 'abc', secure=True, comment='comment')
        response.expireCookie('expires')
        status, headers, result = helper.map_result('foo')
        self.assertEqual(headers[0],
                         ('Set-Cookie', 'comment="abc"; Comment=abc'))
        self.assertEqual(headers[1],
                         ('Set-Cookie', 'domain="abc"; Domain=www.example.com'))
        self.assertEqual(headers[2],
                         ('Set-Cookie',
                          ('expires="deleted"; Max-Age=0; '
                          'Expires=Wed, 31-Dec-97 23:59:59 GMT')))
        self.assertEqual(headers[3],
                         ('Set-Cookie', 'max_age="abc"; Max-Age=1'))
        self.assertEqual(headers[4],
                         ('Set-Cookie', 'multi="abc"; Comment=comment; Secure')
                         )
        self.assertEqual(headers[5],('Set-Cookie', 'path="abc"; Path=/foo/bar'))
        self.assertEqual(headers[6],
                         ('Set-Cookie', 'secure="abc"; Secure'))

    def test_map_result_not_iterable(self):
        class NotIterable:
            pass
        helper = self._makeOne()
        response = helper.request.response
        response.headers['status'] = '200 OK'
        response.headers['content-type'] = 'text/html'
        self.assertRaises(ValueError, helper.map_result, NotIterable)

    def test_map_result_adds_accumulated_headers_to_headers(self):
        helper = self._makeOne()
        response = helper.request.response
        response.accumulated_headers = 'Foo: bar\nFuz: baz\n'
        status, headers, result = helper.map_result('foo')
        self.assertEqual(len(headers), 4)
        self.assertEqual(headers[0],
                         ('Content-Length', '3'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(headers[2],
                         ('Foo', 'bar'))
        self.assertEqual(headers[3],
                         ('Fuz', 'baz'))

    def test_handle_exception_reraises_unknown(self):
        helper = self._makeOne()
        class MyException(Exception):
            pass
        exc_info = (MyException, MyException('foo'), None)
        self.assertRaises(MyException, helper.handle_exception, exc_info)

    def test_handle_exception_unauthorized_string(self):
        helper = self._makeOne()
        helper.request.response.status = '200 OK'
        exc_info = ('Unauthorized', 'foo', None)
        status, headers, body = helper.handle_exception(exc_info)
        self.assertEqual(status, 401)
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], ('Content-Length', '3'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(body, ['foo'])

    def test_handle_exception_unauthorized_zexceptions(self):
        helper = self._makeOne()
        from zExceptions import Unauthorized
        helper.request.response.status = '200 OK'
        exc_info = (Unauthorized, Unauthorized('foo'), None)
        status, headers, body = helper.handle_exception(exc_info)
        self.assertEqual(status, 401)
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], ('Content-Length', '51'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(
            body,
            ["You are not allowed to access 'foo' in this context"])

    def test_handle_exception_unauthorized_accesscontrol(self):
        helper = self._makeOne()
        from AccessControl import Unauthorized
        exc_info = (Unauthorized, Unauthorized('foo'), None)
        status, headers, body = helper.handle_exception(exc_info)
        self.assertEqual(status, 401)
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], ('Content-Length', '51'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(
            body,
            ["You are not allowed to access 'foo' in this context"])

    def test_handle_exception_unauthorized_zexceptions_value_correct(self):
        helper = self._makeOne()
        from zExceptions import Unauthorized
        exc_info = (Unauthorized, Unauthorized('You arent authorized'), None)
        status, headers, body = helper.handle_exception(exc_info)
        self.assertEqual(status, 401)
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], ('Content-Length', '20'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(body, ['You arent authorized'])

    def test_handle_exception_unauthorized_acesscontrol_value_correct(self):
        helper = self._makeOne()
        from AccessControl import Unauthorized
        exc_info = (Unauthorized, Unauthorized('You arent authorized'), None)
        status, headers, body = helper.handle_exception(exc_info)
        self.assertEqual(status, 401)
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], ('Content-Length', '20'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(body, ['You arent authorized'])

    def test_handle_exception_unauthorized_string_value_correct(self):
        helper = self._makeOne()
        exc_info = ('Unauthorized', 'You arent authorized', None)
        status, headers, body = helper.handle_exception(exc_info)
        self.assertEqual(status, 401)
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[0], ('Content-Length', '20'))
        self.assertEqual(headers[1],
                         ('Content-Type', 'text/plain; charset=utf-8'))
        self.assertEqual(body, ['You arent authorized'])

    def test_handle_exception_redirect_string(self):
        helper = self._makeOne()
        exc_info = ('Redirect', 'http://example.com', None)
        self.assertRaises(httpexceptions.HTTPFound,
                          helper.handle_exception, exc_info)

    def test_handle_exception_redirect_class(self):
        helper = self._makeOne()
        from zExceptions import Redirect
        exc_info = (Redirect, Redirect('http://example.com'), None)
        self.assertRaises(httpexceptions.HTTPFound,
                          helper.handle_exception, exc_info)

    def test_handle_exception_redirect_class_value_correct(self):
        helper = self._makeOne()
        from zExceptions import Redirect
        exc_info = (Redirect, Redirect('http://example.com'), None)
        try:
            helper.handle_exception(exc_info)
        except:
            t, v = sys.exc_info()[:2]
            self.assertEqual(t, httpexceptions.HTTPFound)
            headers = v.headers
            self.assertEqual(len(headers), 1)
            headername, header = headers[0]
            self.assertEqual(headername, 'Location')
            self.assertEqual(header, 'http://example.com')
        else:
            raise AssertionError('no redirect')

    def test_handle_exception_redirect_string_value_correct(self):
        helper = self._makeOne()
        exc_info = ('Redirect', 'http://example.com', None)
        try:
            helper.handle_exception(exc_info)
        except:
            t, v = sys.exc_info()[:2]
            self.assertEqual(t, httpexceptions.HTTPFound)
            headers = v.headers
            self.assertEqual(len(headers), 1)
            headername, header = headers[0]
            self.assertEqual(headername, 'Location')
            self.assertEqual(header, 'http://example.com')
        else:
            raise AssertionError('no redirect')

    def test_handle_exception_view(self):
        helper = self._makeOne()
        
        class DummyException(Exception):
            pass
        
        from Products.Five.browser import BrowserView
        from zope.interface import implementsOnly, Interface
        from zope.component import adapts, provideAdapter
        
        # fake doom support if we don't have it in the test build
        import transaction
        if not hasattr(transaction, 'doom'):
            def doom():
                self._doomed = True
            def isDoomed():
                return getattr(self, '_doomed', False)
            transaction.doom = doom
            transaction.isDoomed = isDoomed
        
        class ViewForDummy(BrowserView):
            adapts(DummyException, Interface)
            implementsOnly(Interface)
            
            def __call__(self):
                return "exception"
        
        provideAdapter(ViewForDummy, name="index.html")
        
        exc_info = (DummyException, DummyException(), None)
        status, headers, result = helper.handle_exception(exc_info)
        
        self.failUnless(transaction.isDoomed())
        self.assertEquals('200 OK', status)
        self.assertEquals([('Content-Length', '9'), ('Content-Type', 'text/plain; charset=utf-8')], headers)
        self.assertEquals(['exception'], result)
    
    def test_handle_exception_no_view(self):
        helper = self._makeOne()
        
        class DummyException(Exception):
            pass
        
        exc_info = (DummyException, DummyException(), None)
        
        try:
            helper.handle_exception(exc_info)
            self.fail()
        except DummyException:
            pass
                
    def test__del__tm_not_active(self):
        helper = self._makeOne()
        conn = DummyConnection(None)
        helper.conn = conn
        from StringIO import StringIO
        io = StringIO()
        helper.environ['wsgi.errors'] = io
        del helper
        self.assertEqual(io.getvalue(),
                         'repoze.tm not active; transaction uncommitted\n')
        self.assertEqual(conn.closed, True)
        
    def test__del__tm_active(self):
        helper = self._makeOne()
        conn = DummyConnection(None)
        helper.conn = conn
        from StringIO import StringIO
        io = StringIO()
        helper.environ['wsgi.errors'] = io
        helper.environ['repoze.tm.active'] = True
        del helper
        self.assertEqual(io.getvalue(), '')
        self.assertEqual(conn.closed, False)
        
