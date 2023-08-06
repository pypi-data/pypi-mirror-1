import unittest

class FinderTests(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.zope2.scripts.finder import ZopeFinder
        return ZopeFinder

    def _makeOne(self, argv):
        return self._getTargetClass()(argv)

    def test_get_zope_conf_from_environ(self):
        finder = self._makeOne(['foo'])
        import os
        try:
            os.environ['ZOPE_CONF'] = '/foo/zope.conf'
            self.assertEqual(finder.get_zope_conf(), '/foo/zope.conf')
        finally:
            del os.environ['ZOPE_CONF']
            
    def test_get_zope_conf_from_console_script_path(self):
        finder = self._makeOne(['/bin/runzope'])
        self.assertEqual(finder.get_zope_conf(), '/etc/zope.conf')

class AdduserTests(unittest.TestCase):
    def _getFUT(self):
        from repoze.zope2.scripts.adduser import adduser
        return adduser

    def test_it(self):
        app = DummyApp()
        app.acl_users = DummyUserFolder()
        fn = self._getFUT()
        result = fn(app, 'chris', '123')
        self.assertEqual(result, 'OK')
        self.assertEqual(app.acl_users.user, 'chris')
        self.assertEqual(app.acl_users.pwd, '123')
        self.assertEqual(app.acl_users.roles, ['Manager'])
        self.assertEqual(app.acl_users.domains, [])

class DummyApp:
    pass

class DummyUserFolder:
    def _doAddUser(self, user, pwd, roles, domains):
        self.user = user
        self.pwd = pwd
        self.roles = roles
        self.domains = domains
        return 'OK'
        
