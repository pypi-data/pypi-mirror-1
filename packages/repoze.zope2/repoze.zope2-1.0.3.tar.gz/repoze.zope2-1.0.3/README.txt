Overview

  repoze.zope2 is a decomposition of the Zope 2 appserver publication
  machinery (ZPublisher) into a WSGI application component.  It relies
  on separately-distributed middleware pieces to perform some of the
  features previously handled by ZPublisher and other parts of Zope 2.

Installing repoze.zope2

  With a Python 2.4 interpreter >= 2.4.3 (**Python 2.5+ is
  unsupported**) with setuptools installed, install the 'virtualenv'
  package::

    $PYTHONHOME/bin/easy_install virtualenv

  When this is done, create a virtualenv "sandbox" to hold the
  repoze.zope2 packages and instance data:

    $PYTHONHOME/bin/virtualenv --no-site-packages /path/to/sandbox

  A directory named 'sandbox' will be created in the /path/to.
  directory.  You can use any path you like.

  After creating a virtualenv sandbox, install the 'repoze.zope2' egg
  into the virtualenv.

    /path/to/sandbox/bin/easy_install -i http://dist.repoze.org/simple repoze.zope2

  NOTE: Some "Syntax Error" messages may be printed to the console
  during this process; these can be ignored.  This is distutils
  attempting to byte-compile Zope "Python Scripts" in skin directories
  that aren't valid Python syntax.  

  After the repoze.zope2 packages are installed into the virtualenv,
  you can finally create "instance" files (config files) within the
  sandbox by running "mk2zope2instance"::

    /path/to/sandbox/bin/mkzope2instance

  After these steps have been performed, here's what has happened::

  - a "virtual Python" has been installed within the
    "/path/to/sandbox" directory.  Packages installed to this virtual
    Python's 'site-packages' directory will not conflict with packages
    installed into your "normal" Python's 'site-packages' directory.

  - All packages required by repoze.zope2 have beeen downloaded,
    compiled, and installed as Python eggs in the *virtual* Python's
    'site-packages' directory.

  - 'Products', 'logs', 'var', and 'etc' directories have been created
    inside the sandbox directory.  'Products' is where 3rd party Zope
    products should be installed.  'logs' is where Zope logs will go,
    'var' is where ZODB data files will go, 'etc' is where config
    files are placed.

  - A sample set of configuration files have been installed into the
    sandbox directory's 'etc' subdirectory.  These include::

    - 'zope.ini', a Paste configuration file used to establish the
      Paste (WSGI) pipeline which repoze.zope2 will use to serve up
      repoze.zope2.

    - 'zope.conf', a classic Zope 2 configuration file which can be
      used to adjust Zope settings.

    - 'site.zcml', a boilerplate site.zcml that should be used to
      control ZCML processing.

The Default Sandbox Configuration

  The configuration of WSGI components in the sandbox setup form a
  publishing environment in which most Zope applications should be
  able to run without modification.  Some of the jobs previously
  filled by components in Zope have been assumed by repoze and other
  WSGI middleware components:

  - The job of ZServer has been filled by the zope 3 WSGI server (via
    repoze.zope2.server).

  - The job of ZPublisher object publishing has been filled by the
    object publisher in repoze.zope2

  - The job of ZPublisher transaction management has been filled by
    repoze.tm middleware.

  - The Zope 2 "error_log" has been replaced with error-catching /
    error-logging middleware in Paste.  (Visit /__error_log__ to see
    the exception history).

  - "access" logging can now be handled by a middleware component.

  - The job of VirtualHostMonster is now filled by repoze.vhm.

Utilities

  These utilities are available in the "bin/" directory of the
  generated sandbox.

  installproduct -- provided the directory path of a classic Zope 2
  Product (unpacked), installproduct will attempt to convert the
  product into a Python egg and install it into the sandbox's
  site-packages directory.  This is an alternative to unpacking
  putting the product inside the sandbox "Products" directory.

  addzope2user -- script which adds a management user to the Zope root
  user folder.

  runzope2script -- script which runs a Python script with the root
  Zope application object as the "app" object in the globals
  namespace.

  debugzope2 -- runs the Python interactive interpreter with the Zope
  root object bound to the "app" name in the global dictionary/

  mkzope2instance -- create zope2 instance files in a directory.

Testing repoze.zope2

  To all run repoze.zope2 tests, after running setup.py sandbox, cd to
  the repoze.zope2 directory and run::

    $sandboxdir/bin/python setup.py test

Starting repoze.zope2

  To start a server that serves up a demo app on port 8080, cd to the
  sandbox directory you created via "setup.py sandbox" and run::

    bin/paster serve etc/zope2.ini

  When you visit http://localhost:8080/ in a browser, you should see
  the Zope 2 quickstart page.

  To manage the resulting Zope 2 site, you'll need to add a
  management user.  From the sandbox directory, run::

    bin/zope2adduser <username> <password>

  Once this is done, you should be able to visit
  http://localhost:8080/manage and log in with the username and
  password you supplied.

Deploying

  Due to its simplicity, the default "sandbox" server is preferred for
  development and for some forms of deployment, but to make life
  easier for people more experienced with Apache technologies than
  Zope technologies, a reasonable deployment target for repoze.zope2
  is Apache via "mod_wsgi":http://code.google.com/p/modwsgi/ .
  mod_wsgi is an Apache module that allows you to run WSGI
  applications using the Apache HTTP server.

  A sample ".wsgi" deployment script (an analogue of the ones
  described in the mod_wsgi documentation) is available in the
  doc/sample_zope2.wsgi file.  A sample Apache configuration which
  uses this deployment script is included in the
  doc/sample_apache2.conf file.

  It's suggested that you serve up repoze.zope2 with mod_wsgi in
  "daemon mode" where each if the mod_wsgi's daemon children runs a
  single-threaded Zope process.  All of the Zope processes should
  communicate with a single ZEO server on the back end.  You can run a
  ZEO server by invoking "bin/zeoctl start -C etc/zeo.conf" from
  within a Repoze sandbox.  You'll need to change etc/zope.conf,
  uncommenting the <zodb_db> section that refers to a client storage
  at that point for Zope to work.



  

