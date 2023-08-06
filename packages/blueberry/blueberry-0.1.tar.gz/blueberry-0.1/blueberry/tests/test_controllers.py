import urllib
from blueberry.tests import TestController

class TestMainController(TestController):

    def test_index_get(self):
        response = self.app.get('/')
        assert '200 OK' == response.status

    def test_index_post(self):
        args = dict(
            email='david@alwaysmovefast.com')

        response = self.app.post('/', urllib.urlencode(args))
        assert '200 OK' == response.status
        assert 'david@alwaysmovefast.com' in response

    def test_redirect_get(self):
        response = self.app.get('/redirect')
        assert '302 Found' == response.status

        location = response.headers.get('Location')
        response = self.app.get(location)
        assert 'AcceptRedirect' in response

class TestTagsController(TestController):

    def test_show_get(self):
        response = self.app.get('/tags/python')
        assert '200 OK' == response.status
        assert 'python' in response

class TestFormsController(TestController):

    def test_index_get(self):
        response = self.app.get('/forms')
        assert '200 OK' == response.status

    def test_index_valid_post(self):
        args = dict(
            username='david',
            password='qwerty',
            confirm_password='qwerty')

        response = self.app.post('/forms', urllib.urlencode(args))
        assert '200 OK' == response.status
        assert 'david' in response

    def test_index_invalid_post(self):
        args = dict(
            username='david',
            password='qwerty',
            confirm_password='qwerty123')

        response = self.app.post('/forms', urllib.urlencode(args))
        assert '200 OK' == response.status
        assert 'Errors' in response
