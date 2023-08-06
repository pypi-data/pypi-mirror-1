import unittest

_root = {}

class TestGetDB(unittest.TestCase):
    def setUp(self):
        self.root = _root

        class FakeZopeOptions:
            configroot = None
            confighandlers = None
            def realize(self, args, doc, raise_getopt_errs):
                self.realized = True

        options = FakeZopeOptions()
        self.options = options

        class FakeStartupOptions:
            def ZopeOptions(self):
                return options

        class FakeStarter:
            def setConfiguration(self, configroot):
                self.configroot = configroot
            def setupInitialLogging(self):
                self.setup_initial_logging = True
            def setupSecurityOptions(self):
                self.security_setup = True
            def setupPublisher(self):
                self.publisher_setup = True
            def setupFinalLogging(self):
                self.setup_final_logging = True

        starter = FakeStarter()
        self.starter = starter

        class FakeStartupHandlers:
            def handleConfig(self, configroot, confighandlers):
                self.configroot = configroot
                self.confighandlers = confighandlers

        class FakeStartup:
            options = FakeStartupOptions()
            handlers = FakeStartupHandlers()
            def get_starter(self):
                return starter

        startup = FakeStartup()
        self.startup = startup

        class FakeZope2AppStartup:
            def startup(self):
                self.started = True

        appstartup = FakeZope2AppStartup()
        self.appstartup = appstartup

        class FakeZope2App:
            startup = appstartup

        zope2app = FakeZope2App()

        class FakeConn:
            def root(self):
                return _root

            def close(self):
                self.closed = True

        conn = FakeConn()
        self.conn = conn

        class FakeDB:
            def open(self):
                return conn

        db = FakeDB()
        self.db = db

        class FakeZope2:
            Startup = startup
            App = FakeZope2App()
            DB = db
            bobo_application = 1
            zpublisher_transactions_manager = 1

        zope2 = FakeZope2()
        self.zope2 = zope2

        class FakeZope2Startup:
            pass

        class FakeAppConfig:
            def setConfiguration(self, configroot):
                self.configroot = configroot

        class FakeApp:
            config = FakeAppConfig()

        app = FakeApp()

        class FakeOFSApplicationApplication:
            pass

        dbapp = FakeOFSApplicationApplication()
        self.dbapp = dbapp

        class FakeOFSApplication:
            def Application(self):
                return dbapp

        class FakeOFS:
            Application = FakeOFSApplication()

        class FakeTransaction:
            committed = False
            def commit(self):
                self.committed = True

        txn = FakeTransaction()
        self.txn = txn

        import Zope2
        import Zope2.App
        import Zope2.App.startup
        import App
        import App.config
        import OFS
        import OFS.Application
        import transaction
        self.old = (Zope2, Zope2.App, Zope2.App.startup,
                    App, App.config, OFS, OFS.Application, transaction)
        import sys
        sys.modules['Zope2'] = zope2
        sys.modules['Zope2.App'] = zope2.App
        sys.modules['Zope2.App.startup'] = appstartup
        sys.modules['App'] = app
        sys.modules['App.config'] = app.config
        sys.modules['OFS'] = FakeOFS
        sys.modules['OFS.Application'] = FakeOFSApplication()
        sys.modules['transaction'] = txn

    def tearDown(self):
        import sys
        sys.modules['Zope2'] = self.old[0]
        sys.modules['Zope2.App'] = self.old[1]
        sys.modules['Zope2.App.startup'] = self.old[2]
        sys.modules['App'] = self.old[3]
        sys.modules['App.config'] = self.old[4]
        sys.modules['OFS'] = self.old[5]
        sys.modules['OFS.Application'] = self.old[6]
        sys.modules['transaction'] = self.old[7]
        del self.old
        _root.clear()

    def _getFUT(self):
        from repoze.zope2.db import getDB
        return getDB
        
    def test_getDB_appmissing(self):
        config = {'zope.conf':None, 'appname':'MyApp'}
        f = self._getFUT()
        db = f(config)
        self.assertEqual(len(self.root), 1)
        self.assertEqual(self.root['MyApp'], self.dbapp)
        self.assertEqual(db, self.db)
        self.assertEqual(self.zope2.bobo_application, None)
        self.assertEqual(self.zope2.zpublisher_transactions_manager, None)
        self.assertEqual(self.txn.committed, True)
        self.assertEqual(self.options.realized, True)
        self.assertEqual(self.starter.configroot, None)
        self.assertEqual(self.starter.setup_initial_logging, True)
        self.assertEqual(self.starter.security_setup, True)
        self.assertEqual(self.starter.publisher_setup, True)
        self.assertEqual(self.starter.setup_final_logging, True)
        self.assertEqual(self.conn.closed, True)
        self.assertEqual(self.appstartup.started, True)
        
    def test_getDB_appexists(self):
        config = {'zope.conf':None, 'appname':'MyApp'}
        _root['MyApp'] = True
        f = self._getFUT()
        db = f(config)
        self.assertEqual(_root['MyApp'], True)
        self.assertEqual(self.txn.committed, False)
        
        
        

