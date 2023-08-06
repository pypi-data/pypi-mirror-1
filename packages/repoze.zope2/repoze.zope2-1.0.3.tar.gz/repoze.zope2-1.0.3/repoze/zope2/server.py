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

""" A Paste-compatible constructor for creating a ZServer WSGI HTTP server """

# Use the WSGI component of the zope3 reimplementation of ZServer

import re
import sys
import traceback

from zope.server.http import wsgihttpserver

class ZServer(wsgihttpserver.WSGIHTTPServer):
    def executeRequest(self, task, stderr=sys.stderr):
        """Overrides WSGIHTTPServer's executeRequest so it accepts the
        optional exc_info argument (although it does nothing with it) """
        env = task.getCGIEnvironment()
        env['wsgi.input'] = task.request_data.getBodyStream()

        # fix up noncompliant keys
        env['CHANNEL_CREATION_TIME'] = str(env['CHANNEL_CREATION_TIME'])
        env['QUERY_STRING'] = env.get('QUERY_STRING', '')

        # extend wsgihttpserver environment with PEP-333-mandated envvars
        env['wsgi.version'] = (1,0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.errors'] = stderr
        env['wsgi.multithread'] = 1
        env['wsgi.multiprocess'] = 0
        env['wsgi.run_once'] = 0

        def start_response(status, headers, exc_info=None):
            # Prepare the headers for output
            status, reason = re.match('([0-9]*) (.*)', status).groups()
            task.setResponseStatus(status, reason)
            task.appendResponseHeaders(['%s: %s' % i for i in headers])

            # Return the write method used to write the response data.
            return wsgihttpserver.fakeWrite

        # Call the application to handle the request and write a response
        iterator = self.application(env, start_response)
        task.write(iterator)
        if hasattr(iterator, 'close'):
            try:
                iterator.close()
            except:
                traceback.print_exc(file=env['wsgi.errors'])

def get_zserver(wsgi_app, host, port, threads):
    from zope.server.taskthreads import ThreadedTaskDispatcher
    td = ThreadedTaskDispatcher()
    td.setThreadCount(int(threads))
    server = ZServer(wsgi_app, ip=host, port=int(port), task_dispatcher=td)
    return server

def run_zserver(wsgi_app, global_conf, host='localhost', port=8080, threads=4):
    import asyncore
    server = get_zserver(wsgi_app, host, port, threads)
    print 'zserver on port %s' % port
    while 1:
        asyncore.poll(5)

