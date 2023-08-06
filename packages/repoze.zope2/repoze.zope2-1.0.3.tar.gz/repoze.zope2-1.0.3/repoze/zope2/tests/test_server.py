import unittest

class ServerTests(unittest.TestCase):
    def test_get_zserver1(self):
        from repoze.zope2.server import get_zserver
        server = get_zserver(None, 'localhost', 66666, 20)
        server.close()
        self.assertEqual(server.application, None)
        self.assertEqual(server.server_name, 'localhost')
        self.assertEqual(server.port, 66666)
        self.assertEqual(len(server.task_dispatcher.threads), 20)
        
    def test_get_zserver2(self):
        from repoze.zope2.server import get_zserver
        server = get_zserver(None, 'localhost', '66666', '20')
        server.close()
        self.assertEqual(server.application, None)
        self.assertEqual(server.server_name, 'localhost')
        self.assertEqual(server.port, 66666)
        self.assertEqual(len(server.task_dispatcher.threads), 20)

    def test_zserver_executeRequest_closes_app_iter(self):
        from repoze.zope2.server import ZServer
        host = 'localhost'
        port = '199764'
        td = None
        from StringIO import StringIO
        io = StringIO()
        wsgi_app = FakeApp(io)
        server = ZServer(wsgi_app, ip=host, port=int(port), task_dispatcher=td)
        try:
            env = {'CHANNEL_CREATION_TIME':1}
            task = FakeTask(env)
            server.executeRequest(task)
            self.assertEqual(io.closed, True)
        finally:
            server.close()

    def test_zserver_executeRequest_app_iter_close_raises(self):
        from repoze.zope2.server import ZServer
        host = 'localhost'
        port = '199764'
        td = None
        from StringIO import StringIO
        io = StringIO()
        def close():
            raise ValueError, 'foo'
        io.close = close
        wsgi_app = FakeApp(io)
        server = ZServer(wsgi_app, ip=host, port=int(port), task_dispatcher=td)
        try:
            env = {'CHANNEL_CREATION_TIME':1}
            task = FakeTask(env)
            errors = StringIO()
            server.executeRequest(task, errors)
            self.assertEqual(io.closed, False)
            errorval = errors.getvalue()
            self.failUnless(errorval.find('ValueError')!=-1, errorval)
        finally:
            server.close()

class FakeRequestData:
    def getBodyStream(self):
        from StringIO import StringIO
        return StringIO()

class FakeTask:
    def __init__(self, env):
        self.env = env
        self.request_data = FakeRequestData()
    def getCGIEnvironment(self):
        return self.env
    def write(self, app_iter):
        self.app_iter = app_iter
    
class FakeApp:
    def __init__(self, io):
        self.io = io
    def __call__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        return self.io
        
        
