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

import unittest
from paste import httpexceptions
from repoze.zope2.tests.base import DummyPublishedObject
from repoze.zope2.tests.base import DummyGetitemPublishedObject
from repoze.zope2.tests.base import DummyBoboTraversePublishedObject
from repoze.zope2.tests.base import DummyGetattrPublishedObject
from repoze.zope2.tests.base import DummyBrowserDefaultPublishedObject
from repoze.zope2.tests.base import DummyRequest

class DefaultPublishTraverseTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.zope2.publishtraverse import DefaultPublishTraverse
        return DefaultPublishTraverse

    def _makeOne(self, context, request):
        return self._getTargetClass()(context, request)

    def test_publishTraverse_underscore(self):
        context = DummyPublishedObject()
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertRaises(httpexceptions.HTTPForbidden,
                          dpt.publishTraverse, request, '_hi')
        
    def test_publishTraverse_getitem_nodocstring(self):
        context = DummyGetitemPublishedObject()
        sub = DummyPublishedObject()
        context.subs['hi'] = sub
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertRaises(httpexceptions.HTTPForbidden,
                          dpt.publishTraverse, request, 'hi')
    

    def test_publishTraverse_getitem_withdocstring(self):
        context = DummyGetitemPublishedObject()
        sub = DummyPublishedObject()
        sub.__doc__ = 'yup'
        context.subs['hi'] = sub
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertEqual(dpt.publishTraverse(request, 'hi'), sub)
    
    def test_publishTraverse_getitem_withnamedocstring(self):
        context = DummyGetitemPublishedObject()
        sub = DummyPublishedObject()
        context.hi__doc__ = 'yup'
        context.subs['hi'] = sub
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertEqual(dpt.publishTraverse(request, 'hi'), sub)

    def test_publishTraverse_getitem_typecheckfail(self):
        context = DummyGetitemPublishedObject()
        sub = []
        context.subs['hi'] = sub
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertRaises(httpexceptions.HTTPForbidden,
                          dpt.publishTraverse, request, 'hi')

    def test_publishTraverse_bobotraverse_returns_object(self):
        context = DummyBoboTraversePublishedObject()
        sub = DummyPublishedObject()
        sub.__doc__ = 'yup'
        context.subs['hi'] = sub
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertEqual(dpt.publishTraverse(request, 'hi'), sub)

    def test_publishTraverse_bobotraverse_raises(self):
        context = DummyBoboTraversePublishedObject()
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        try:
            from zope.traversing.interfaces import TraversalError
        except ImportError:
            from zope.app.traversing.interfaces import TraversalError
        self.assertRaises(TraversalError, dpt.publishTraverse, request, 'hi')
    
    def test_publishTraverse_getattr(self):
        context = DummyGetattrPublishedObject()
        sub = DummyPublishedObject()
        sub.__doc__ = 'yup'
        context.subs['hi'] = sub
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        self.assertEqual(dpt.publishTraverse(request, 'hi'), sub)

    def test_publishTraverse_no_getitem_getattr_or_bt(self):
        context = DummyPublishedObject()
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        try:
            from zope.traversing.interfaces import TraversalError
        except ImportError:
            from zope.app.traversing.interfaces import TraversalError
        self.assertRaises(TraversalError, dpt.publishTraverse, request, 'hi')

    def test_publishTraverse_returns_null_resource_when_no_trns(self):
        from webdav.NullResource import NullResource
        from Acquisition import Implicit
        class AqAwareDummyPublishedObject(Implicit, DummyPublishedObject):
            aq_base = 1
        context = AqAwareDummyPublishedObject()
        request = DummyRequest({'URL':'http://www.example.com',
                                'TraversalRequestNameStack':[]})
        dpt = self._makeOne(context, request)
        request.no_acquire_flag = True
        result = dpt.publishTraverse(request, 'foo')
        self.failUnless(isinstance(result, NullResource), result)

    def test_browserDefault_with_bd(self):
        context = DummyBrowserDefaultPublishedObject()
        context.browserdefault = DummyPublishedObject()
        request = DummyRequest({'URL':'http://www.example.com'})
        dpt = self._makeOne(context, request)
        result = dpt.browserDefault(request)
        self.assertEqual(result[0], context.browserdefault)
        self.assertEqual(result[1], ())

    # TODO:
    # test when __bobo_traverse__ raises Att/Key/NotFound and we
    #   try to find a view, and the view lookup suceeds
    # test when we try __getattr__(aq_base) but it fails, so we fall back to
    #   finding a view, and it succeeds
    # test when we try __getattr__(aq_base) and it fails, and subsequent
    #   try to find a view fails, so we try to acquire the attr
    # test browserDefault when we try queryDefaultViewName
