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

""" Utilities for constructing Zope request and response objects """

from ZPublisher.HTTPRequest import HTTPRequest

from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPResponse import status_codes
from ZPublisher.HTTPResponse import status_reasons

from tempfile import NamedTemporaryFile

class RepozeHTTPResponse(HTTPResponse):
    def write(self, data):
        """
        Override HTTPResponse.write in order to prevent it from writing
        headers to output (we'll do that later).
        """
        self._wrote = True
        self.stdout.write(data)

def makeRequest(environ):
    temp = NamedTemporaryFile()
    response = RepozeHTTPResponse(stdout=temp)
    stdin = environ['wsgi.input']
    # The clean = True argument is important.  If we don't pass it,
    # our WSGI environment is copied and replaced, and thus we won't
    # be able to mutate it successfully within the application.
    request = HTTPRequest(stdin, environ, response, clean=True)
    request.no_acquire_flag = False # used by DefaultPublishTraverse
    return request

def convertResponseCode(code_or_reason):
    if isinstance(code_or_reason, str):
        code_or_reason = code_or_reason.lower()
    code = status_codes.get(code_or_reason, 500)
    reason = status_reasons.get(code, 'Unknown')
    return code, reason

    
