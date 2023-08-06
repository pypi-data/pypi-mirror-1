# from webunit import webunittest
from kforge.external.wsgi_webunit import webunittest
import kforge.external.wsgi_intercept as wsgi_intercept
import django.core.handlers.wsgi
from httplib import HTTP

from kforge.external.wsgi_intercept import WSGI_HTTPConnection
class WSGI_HTTP(HTTP):
    _connection_class = WSGI_HTTPConnection

class DemoTest(webunittest.WebTestCase):

    scheme_handlers = dict(http=WSGI_HTTP)
    # host = 'local.kforge.net'
    host = '127.0.0.1'
    port = 8050

    def setUp(self):
        self.setServer(self.host, self.port)
        # just will not work ...
        # wsgi_app = django.core.handlers.wsgi.WSGIHandler()
        # wsgi_intercept.add_wsgi_intercept(self.host, self.port, lambda: wsgi_app)
   
    def tearDown(self):
        # wsgi_intercept.remove_wsgi_intercept(self.host, self.port)
        pass

    def test_1(self):
        out = self.page('/') 
        print out

if __name__ == '__main__':
    unittest.main()
