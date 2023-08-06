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

__version__ = '1.0.3'

from ez_setup import use_setuptools
use_setuptools()

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='repoze.zope2',
      version=__version__,
      description='Zope2 via WSGI and Paste',
      long_description=README + '\n\nCHANGES\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='web application server wsgi zope',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      tests_require = [
               'zopelib',
               'repoze.tm',
               'repoze.errorlog',
               'repoze.vhm',
               'repoze.retry',
               'repoze.obob',
               ],
      install_requires=[
               'setuptools',
               'PasteScript',
               'WSGIUtils',
               'zopelib',
               'repoze.obob',
               'repoze.tm',
               'repoze.retry',
               'repoze.vhm',
               'repoze.errorlog',
               ],
      test_suite="repoze.zope2.tests",
      entry_points = """\
        [console_scripts]
        addzope2user = repoze.zope2.scripts.adduser:main
        runzope2script = repoze.zope2.scripts.runscript:main
        debugzope2 = repoze.zope2.scripts.debug:main
        installproduct = repoze.zope2.scripts.installproduct:main
        mkzope2instance = repoze.zope2.instance:main
        zope2testrunner = repoze.zope2.scripts.testrunner:main

        [paste.server_runner]
        zserver = repoze.zope2.server:run_zserver

        [repoze.project]
        initialize = repoze.zope2.instance:mkinstance
      """,
      )

