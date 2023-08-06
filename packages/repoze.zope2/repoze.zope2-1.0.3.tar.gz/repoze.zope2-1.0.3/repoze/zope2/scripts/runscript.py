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

""" Run a Python script with the Zope application object in globals as 'app' """

import sys
from repoze.zope2.scripts.finder import ZopeFinder

def main(argv=sys.argv):
    # run a script with arguments with 'app' in the globals namespace
    finder = ZopeFinder(argv)
    me = argv.pop(0)
    if not len(argv):
        raise ValueError("must be called with a script name as first argument")
    app = finder.get_app()
    g = globals()
    g['app'] = app
    execfile(argv[0], g)

if __name__ == '__main__':
    main()
