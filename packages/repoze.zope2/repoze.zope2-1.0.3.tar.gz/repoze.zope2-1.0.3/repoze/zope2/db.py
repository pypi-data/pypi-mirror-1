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

""" Utilies for constructing a ZODB database object """

def getDB(config):
    config_file = config['zope.conf']
    # these are imported without "from" statements in them so we can
    # unit test them more easily
    import Zope2
    import Zope2.Startup
    import Zope2.Startup.options
    import Zope2.Startup.handlers
    import Zope2.App.startup
    import App.config
    import OFS.Application
    import transaction

    starter = Zope2.Startup.get_starter()
    opts = Zope2.Startup.options.ZopeOptions()
    opts.configfile = config_file
    opts.realize(args=[], doc="", raise_getopt_errs=0)
    Zope2.Startup.handlers.handleConfig(opts.configroot, opts.confighandlers)
    App.config.setConfiguration(opts.configroot)
    starter.setConfiguration(opts.configroot)
    starter.setupInitialLogging()
    starter.setupSecurityOptions()
    starter.setupPublisher()
    # startup is what causes Products to be installed; Product
    # initialization causes database writes, which cause conflict
    # errors when used with multiple clients vs. ZEO.  We need some
    # way to retry these conflict errors.  I wish Zope didn't write to
    # the database at startup time.
    Zope2.App.startup.startup()
    starter.setupFinalLogging()
    Zope2.zpublisher_transactions_manager = None # middleware does this
    # Zope2.bobo_application is used by: App.ZApplication
    # ZPublisher.Publish, ZPublisher.WSGIPublisher,
    # Zope2.__init__, Zope2.App.startup
    Zope2.bobo_application = None
    db = Zope2.DB # set the global
    conn = db.open()
    root = conn.root()
    appname = config.get('appname', 'Application')
    # this can also conflict
    if not root.has_key(appname):
        root[appname] = OFS.Application.Application()
        transaction.commit()
    conn.close()
    return db

