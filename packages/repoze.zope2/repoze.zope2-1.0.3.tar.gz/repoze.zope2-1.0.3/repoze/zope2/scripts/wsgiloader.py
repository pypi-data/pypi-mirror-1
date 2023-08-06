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
"""
Stub for a running repoze.zope2 sandbox under mod_wsgi.  Intended to
be used as a 'WSGIScriptAlias' within the Apache configuration, e.g.::

WSGIPythonExecutable ${sandbox}/bin/python

<Directory ${sandbox}/etc>
  Order deny,allow
  Allow from all
</Directory>

<VirtualHost *:80>
  ServerName www.example.com
  WSGIScriptAlias /site ${sandbox}/bin/zope2.wsgi
  WSGIPassAuthorization On
  SetEnv HTTP_X_VHM_HOST http://www.example.com/site
  SetEnv PASTE_CONFIG ${sandbox}/etc/zope2.ini
</VirtualHost>

"""
import os
import sys

def main():
    # load up the paste pipeline for mod_wsgi

    config = os.environ.get('PASTE_CONFIG')
    if not config:
        # we assume that the console script lives in the 'bin' dir of a sandbox
        me = sys.argv[0]
        sandbox = os.path.dirname(os.path.dirname(os.path.abspath(me)))
        config = os.path.join(sandbox, 'etc', 'zope2.ini')

    from paste.deploy import loadapp
    application = loadapp('config:%s' % config)

if __name__ == '__main__':
    main()
