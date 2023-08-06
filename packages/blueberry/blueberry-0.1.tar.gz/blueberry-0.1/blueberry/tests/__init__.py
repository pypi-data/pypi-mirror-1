import unittest
import webtest
from blueberry import web
from blueberry.tests import routing

class TestController(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        app = web.WSGIApplication(routing.urls)
        self.app = webtest.TestApp(app)
        unittest.TestCase.__init__(self, *args, **kwargs)
