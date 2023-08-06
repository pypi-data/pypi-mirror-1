import base64
import unittest

import mock

class TestLoginRequired(unittest.TestCase):

    @property
    def login_required(self):
        from wheeljack.decorators import login_required
        return login_required

    def request(self):
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        request = HttpRequest()
        request.method = 'PUT'
        request.user = AnonymousUser()

        auth = base64.b64encode('Wheeljack:Lancia Stratos')
        request.META['HTTP_AUTHORIZATION'] = 'basic ' + auth
        return request

    @mock.patch('django.contrib.auth.authenticate')
    @mock.patch('django.contrib.auth.login')
    def test_basic_challenge(self, authenticate, login):
        # When a proper set of credentials is proved we will get through.
        orig = lambda request: 'OK'
        wrapped = self.login_required(orig)
        self.assertEqual(wrapped(self.request()), 'OK')
        authenticate.assert_called_with(username='Wheeljack',
                                        password='Lancia Stratos')
        self.assert_(login.is_called)

    def test_already_authenticated(self):
        # Requests that already have an authenticated user will just get
        # through directly.
        orig = lambda request: 'OK'
        wrapped = self.login_required(orig)
        request = self.request()
        from django.contrib.auth.models import User
        request.user = User()
        self.assertEqual(wrapped(request), 'OK')

    def test_only_basic_auth(self):
        # The API currently only supports basic authentication.
        orig = lambda request: 'OK'
        wrapped = self.login_required(orig)
        request = self.request()
        request.META['HTTP_AUTHORIZATION'] = 'digest somedigest'
        response = wrapped(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content,
                         'Only basic authentication is supported')

    @mock.patch('django.contrib.auth.authenticate')
    def test_invalid_user(self, authenticate):
        # When the API detects an invalid user it will return a forbidden
        # response.
        orig = lambda request: 'OK'
        wrapped = self.login_required(orig)
        request = self.request()
        authenticate.return_value = None
        response = wrapped(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'Invalid user or password')

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestLoginRequired)
            ])
