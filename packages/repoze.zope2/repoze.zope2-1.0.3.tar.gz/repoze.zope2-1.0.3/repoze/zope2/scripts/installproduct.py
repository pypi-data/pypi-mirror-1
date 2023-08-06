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

""" Convert a classic Zope 2 Product into an egg.  Provided a Zope
product directory as its first argument, creates a namespace-packaged
egg with a Python package path of Products.<productname> and installs
it to the site-packages directory of the Python used to invoke this
script.  README.txt becomes the setuptools 'long_description', and
VERSION.txt becomes the setuptools version."""

import os
import sys
import tempfile
import shutil
from setuptools import setup
from setuptools import find_packages
from setuptools.command import egg_info
from setuptools.command import sdist

def nonvc(dirname=''):
    if not dirname:
        dirname = '.'
    for path, dnames, fnames in os.walk(dirname):
        if path.startswith('.'+os.sep):
            path = path[2:]
        for fname in fnames:
            if fname.endswith('.pyc') or fname.endswith('~'):
                continue
            yield os.path.join(path, fname)

def install(name, version, dir, readme):
    cwd = os.getcwd()
    try:
        # this is evil and silly; we temporarily patch the revctrl
        # walking finder to report that "most" files are under version
        # control, even though they're not necessarily under any, so
        # we can make all files in the product "package data"
        old_walk_revctrl = egg_info.walk_revctrl
        egg_info.walk_revctrl = nonvc
        sdist.walk_revctrl = nonvc
        os.chdir(dir)
        setup(
            name='Products.%s' % name,
            version=version,
            description='Zope2 product: %s' % name,
            long_description=readme,
            author='unknown',
            author_email='unknown',
            license='unknown',
            packages=find_packages(dir),
            namespace_packages=['Products'],
            zip_safe=False,
            include_package_data=True,
            )
    finally:
        egg_info.walk_revctrl = old_walk_revctrl
        sdist.walk_revctrl = old_walk_revctrl
        os.chdir(cwd)

def main():
    tmpdir = tempfile.mkdtemp()
    try:
        sourcedir = os.path.abspath(os.path.expanduser(
            os.path.normpath(sys.argv.pop())))
        productsdir = os.path.join(tmpdir, 'Products')
        os.makedirs(productsdir)
        init = open(os.path.join(productsdir, '__init__.py'), 'w')
        init.write("__import__('pkg_resources').declare_namespace(__name__)\n")
        init.close()
        productname = os.path.split(sourcedir)[1]
        productdir = os.path.join(productsdir, productname)
        shutil.copytree(sourcedir, productdir)
        version = 'unknown'
        for name in ('version.txt', 'VERSION.txt', 'version.TXT'):
            vtxt = os.path.join(productdir, name)
            if os.path.exists(vtxt):
                version = open(vtxt).readline().strip()
                break
        description = 'unknown'
        for name in ('readme.txt', 'README.txt', 'readme.TXT'):
            readme = os.path.join(productdir, name)
            if os.path.exists(readme):
                description = open(readme).read()
                break
        sys.argv.append('install')
        install(productname, version, tmpdir, description)
    finally:
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print __doc__
        print "Usage: %s <Zope 2 product directory>"
        sys.exit(255)
    main()
    
