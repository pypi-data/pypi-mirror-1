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

""" Run an interactive Zope debugging session  """

from code import interact
import sys

from repoze.zope2.scripts.finder import ZopeFinder

def main(argv=sys.argv):
    finder = ZopeFinder(argv)
    app = finder.get_app()
    cprt = ('Type "help" for more information. "app" is the Zope application '
            'object.')
    banner = "Python %s on %s\n%s" % (sys.version, sys.platform, cprt)
    interact(banner, local={'app':app})

if __name__ == '__main__':
    main()
