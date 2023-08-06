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

""" Implement Zope publishing traversal """

import types

from paste import httpexceptions

from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPublisher

_BETTER_THAN_210 = True

try:
    # Zope 2.10+
    from zope.traversing.interfaces import TraversalError
except ImportError:
    # 2.9
    from zope.app.traversing.interfaces import TraversalError
    _BETTER_THAN_210 = False

from zope.app.publisher.browser import queryDefaultViewName

from Acquisition import aq_base
from zExceptions import NotFound

from webdav.NullResource import NullResource

class DefaultPublishTraverse(object):

    implements(IBrowserPublisher)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def publishTraverse(self, request, name):
        object = self.context
        URL=request['URL']
        trns = request['TraversalRequestNameStack']

        if name[:1]=='_':
            raise httpexceptions.HTTPForbidden(
                "Object name begins with an underscore at: %s" % URL)
        
        if hasattr(object,'__bobo_traverse__'):
            try:
                subobject = object.__bobo_traverse__(request, name)
                # the ZPublisher implementation of this put additional parents
                # into the path if the subobject was a tuple of greater
                # than length 1.  We don't support that pattern here.
            except (AttributeError, KeyError, NotFound), e:
                # The contract of __bobo_traverse__ is defacto; if it
                # raises an AttributeError, KeyError, or NotFound
                # error, it indicates that the name could not be
                # found.  We turn that into a TraversalError and catch
                # this error in an upper layer.

                # Try to find a view
                subobject = queryMultiAdapter((object, request),
                                              Interface, name)
                if subobject is not None:
                    # OFS.Application.__bobo_traverse__ calls
                    # REQUEST.RESPONSE.notFoundError which sets the HTTP
                    # status code to 404
                    request.response.setStatus(200)
                    # We don't need to do the docstring security check
                    # for views, so lets skip it and return the object here.
                    return subobject.__of__(object)
                # No view found.
                raise TraversalError(name)
        else:
            # No __bobo_traverse__
            # Try with an unacquired attribute:
            if hasattr(aq_base(object), name):
                subobject = getattr(object, name)
            else:
                # We try to fall back to a view:
                subobject = queryMultiAdapter((object, request), name=name)
                if subobject is not None:
                    return subobject.__of__(object)

                # CM: add in custom code for returning a NullResource
                # because we don't do it in the Repoze equivalent of
                # BaseRequest.traverse (it really doesn't belong there)
                if request.no_acquire_flag:
                    # Because this is a WebDAV client, if this is the
                    # last object in the path, it must not be
                    # acquired.  Instead, a NullResource should be
                    # given if it doesn't exist.
                    if not trns and hasattr(object, 'aq_base'):
                        # the hasattr check is just to see if it's
                        # acquisition-aware
                        return NullResource(object,name,request).__of__(
                            object)
                ## /CM

                # And lastly, of there is no view, try acquired attributes, but
                # only if there is no __bobo_traverse__:
                try:
                    subobject=getattr(object, name)
                    # Again, clear any error status created by __bobo_traverse__
                    # because we actually found something:
                    request.response.setStatus(200)
                    return subobject
                except AttributeError:
                    pass

                # Lastly we try with key access:
                # CM: the stock version of publishTraverse doesn't check
                # if the object actually has a __getitem__
                if hasattr(object, '__getitem__'):
                    try:
                        subobject = object[name]
                    except KeyError:
                        raise TraversalError(name)
                else:
                    raise TraversalError(name)

        # Ensure that the object has a docstring, or that the parent
        # object has a pseudo-docstring for the object. Objects that
        # have an empty or missing docstring are not published.
        doc = getattr(subobject, '__doc__', None)
        if doc is None:
            doc = getattr(object, '%s__doc__' % name, None)
        if not doc:
            raise httpexceptions.HTTPForbidden(
                "The object at %s has an empty or missing "
                "docstring. Objects must have a docstring to be "
                "published." % URL
                )

        # Hack for security: in Python 2.2.2, most built-in types
        # gained docstrings that they didn't have before. That caused
        # certain mutable types (dicts, lists) to become publishable
        # when they shouldn't be. The following check makes sure that
        # the right thing happens in both 2.2.2+ and earlier versions.

        if not typeCheck(subobject):
            raise httpexceptions.HTTPForbidden(
                "The object at %s is not publishable." % URL
                )

        return subobject
    
    def browserDefault(self, request):
        if hasattr(self.context, '__browser_default__'):
            return self.context.__browser_default__(request)
        if _BETTER_THAN_210:
            # The 2.9 publisher doesn't do this dance (and breaks
            # when it is done), so we only do this if we're running
            # under 2.10 or better.

            # Zope 3.2 still uses IDefaultView name when it
            # registeres default views, even though it's
            # deprecated. So we handle that here:
            default_name = queryDefaultViewName(self.context, request)
            if default_name is not None:
                # Adding '@@' here forces this to be a view.
                # A neater solution might be desireable.
                return self.context, ('@@' + default_name,)
        return self.context, ()

# This mapping contains the built-in types that gained docstrings
# between Python 2.1 and 2.2.2. By specifically checking for these
# types during publishing, we ensure the same publishing rules in
# both versions. The downside is that this needs to be extended as
# new built-in types are added and future Python versions are
# supported. That happens rarely enough that hopefully we'll be on
# Zope 3 by then :)

itypes = {}
for name in ('NoneType', 'IntType', 'LongType', 'FloatType', 'StringType',
             'BufferType', 'TupleType', 'ListType', 'DictType', 'XRangeType',
             'SliceType', 'EllipsisType', 'UnicodeType', 'CodeType',
             'TracebackType', 'FrameType', 'DictProxyType', 'BooleanType',
             'ComplexType'):
    if hasattr(types, name):
        itypes[getattr(types, name)] = 0

# Python 2.4 no longer maintains the types module.
itypes[set] = 0
itypes[frozenset] = 0

def typeCheck(obj, deny=itypes):
    # Return true if its ok to publish the type, false otherwise.
    return deny.get(type(obj), 1)

