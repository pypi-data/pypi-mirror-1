"""

Stub for running under mod_wsgi.  Intended to be used as a
'WSGIScriptAlias' within the Apache configuration, e.g.::

WSGIScriptAlias /site /path/to/sandbox/etc/zope2.wsgi

""" 
import os
from paste.deploy import loadapp

ini = '${sandbox}/etc/zope2.ini'
application = loadapp('config:%s' % ini)
