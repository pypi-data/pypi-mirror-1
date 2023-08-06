import unittest

class TestMakeRequest(unittest.TestCase):
    def _getFUT(self):
        from repoze.zope2.request import makeRequest
        return makeRequest
        
    def test_makeRequest(self):
        from repoze.zope2.tests.base import _makeEnviron
        makeRequest = self._getFUT()
        environ = _makeEnviron()
        request = makeRequest(environ)
        self.failUnless(request.environ is environ, request.stdin)
        self.failUnless(request.stdin is environ['wsgi.input'])
        self.assertNotEqual(request.response, None)
        from repoze.zope2.request import RepozeHTTPResponse
        self.failUnless(isinstance(request.response, RepozeHTTPResponse))

class TestConvertResponseCode(unittest.TestCase):
    def _getFUT(self):
        from repoze.zope2.request import convertResponseCode
        return convertResponseCode
        
    def test_convertResponseCode(self):
        f = self._getFUT()
        self.assertEqual(f(500), (500, 'Internal Server Error'))
        self.assertEqual(f('Unauthorized'), (401, 'Unauthorized'))

class TestRepozeHTTPResponse(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.zope2.request import RepozeHTTPResponse
        return RepozeHTTPResponse

    def _makeOne(self, stdout):
        return self._getTargetClass()(stdout=stdout)

    def test_write(self):
        from StringIO import StringIO
        stdout = StringIO()
        response = self._makeOne(stdout)
        response.write('hello')
        self.assertEqual(stdout.getvalue(), 'hello')
        self.assertEqual(response._wrote, True)
        response.write(' there')
        self.assertEqual(stdout.getvalue(), 'hello there')
        self.assertEqual(response._wrote, True)
        

    
