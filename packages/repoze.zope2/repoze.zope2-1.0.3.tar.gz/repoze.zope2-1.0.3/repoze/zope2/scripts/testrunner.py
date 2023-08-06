#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope 2 test script

see zope.testing testrunner.txt
"""

import sys
import os

from zope.testing import testrunner
from repoze.zope2.scripts.finder import ZopeFinder

def filter_warnings(option, opt, *ignored):
    import warnings
    warnings.simplefilter('ignore', Warning, append=True)

testrunner.other.add_option(
    '--nowarnings', action="callback", callback=filter_warnings,
    help="Install a filter to suppress warnings emitted by code.")

def main(argv=sys.argv, exit=sys.exit):
    finder = ZopeFinder(argv)
    config_file = finder.get_zope_conf()
    import Zope2
    print 'Parsing %s' % config_file
    Zope2.configure(config_file)
    import App.FindHomes # import for side effects
    ihome = os.getenv('INSTANCE_HOME')
    products = os.path.join(ihome, 'Products')
    defaults = []
    if os.path.exists(products):
        defaults += ['--package-path', products, 'Products']
    # Remove script directory from path:
    scriptdir = os.path.realpath(os.path.dirname(sys.argv[0]))
    sys.path[:] = [p for p in sys.path if os.path.realpath(p) != scriptdir]
    # add parent dir of scriptdir to path
    sys.path.append(os.path.dirname(scriptdir))
    for path in sys.path:
        defaults += ['--test-path', path]
    failed = testrunner.run(defaults + argv[1:])
    if failed:
        exit(1)

if __name__ == '__main__':
    sys.exit(main())
