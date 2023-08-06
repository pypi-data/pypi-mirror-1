import unittest
import base64
from datetime import datetime

import mock

from wheeljack.testing import APITestCase

class TestAPIBase(unittest.TestCase):

    @property
    def api(self):
        from wheeljack.views.api import API
        return API

    def request(self):
        from django.http import HttpRequest
        request = HttpRequest()
        request.method = 'PUT'

        auth = base64.b64encode('Wheeljack:Lancia Stratos')
        request.META['HTTP_AUTHORIZATION'] = 'basic ' + auth
        return request

    @mock.patch('django.contrib.auth.authenticate')
    @mock.patch('django.contrib.auth.login')
    def test_method_no_available_methods(self, authenticate, login):
        # The API base class makes sure that only allowed methods are
        # executed. Any other attempts will return a forbidden response.
        no_methods = self.api()
        request = self.request()

        response = no_methods(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], '')

    @mock.patch('django.contrib.auth.authenticate')
    @mock.patch('django.contrib.auth.login')
    def test_method_not_allowed(self, authenticate, login):
        # The API base class makes sure that only allowed methods are
        # executed. Any other attempts will return a forbidden response.
        class SomeMethods(self.api):
            def post(self, request):
                pass

            def get(self, request):
                pass
        some_methods = SomeMethods()
        request = self.request()

        response = some_methods(request)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], 'get, post')

    def test_only_basic_auth(self):
        # The API currently only supports basic authentication.
        api = self.api()
        request = self.request()
        request.META['HTTP_AUTHORIZATION'] = 'digest somedigest'
        response = api(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content,
                         'Only basic authentication is supported')

    @mock.patch('django.contrib.auth.authenticate')
    def test_invalid_user(self, authenticate):
        # When the API detects an invalid user it will return a forbidden
        # response.
        api = self.api()
        request = self.request()
        authenticate.return_value = None
        response = api(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, 'Invalid user or password')


class TestProjectOverview(APITestCase):

    def setUp(self):
        super(TestProjectOverview, self).setUp()
        from django.core.urlresolvers import reverse
        self.url = reverse('wheeljack.views.project_overview_api')

    def test_project_listing(self):
        # A GET request on the view should return a list of projects.
        self.assertEqualJSON(self.client.get(self.url), {'projects': []})
        # Let's create a project to make this more interesting.
        from wheeljack.models import Project
        Project.objects.create(name='Optimus Prime')
        self.assertEqualJSON(
            self.client.get(self.url),
            {"projects": [{"href": "http://testserver/api/project/1/",
                           "name": "Optimus Prime"}]})

class TestProject(APITestCase):

    def setUp(self):
        super(TestProject, self).setUp()
        # Create an project to test with
        from wheeljack.models import Project
        self.project = Project.objects.create(name='Bumblebee')
        from django.core.urlresolvers import reverse
        self.url = reverse('wheeljack.views.project_api',
                           args=[self.project.pk])

    def test_get(self):
        # A GET request on the view should give us all the info about the
        # project.
        self.assertEqualJSON(
            self.client.get(self.url),
            {"url": "http://testserver/api/project/1/", "build_cmd": "",
             "name": "Bumblebee", "last_revision": "", "vcs": "",
             "require_build": True, "repository": ""})

    def test_last_revision(self):
        # The last revision is determined based on the log entries. No log
        # entry means an empty last revision.
        import simplejson as json
        def get_last_revision():
            return json.loads(self.client.get(self.url).content)[
                'last_revision']
        self.assertEqual(get_last_revision(), '')
        # Creating a log entry should give us the revision from that entry.
        self.project.buildlog_set.create(revision='some rev',
                                         start=datetime.now(),
                                         end=datetime.now())
        self.assertEqual(get_last_revision(), 'some rev')
        # Creating another log entry should make that ones revision the
        # current.
        self.project.buildlog_set.create(revision='some later rev',
                                         start=datetime.now(),
                                         end=datetime.now())
        self.assertEqual(get_last_revision(), 'some later rev')


    def test_put(self):
        # To create a new log entry clients can use a HTTP PUT. By default
        # there are no log entries.
        self.assertEqual(self.project.buildlog_set.count(), 0)
        # Let's create a log entry using HTTP.
        from datetime import datetime
        import simplejson as json
        self.client.put(
            self.url,
            content_type='text/json',
            data=json.dumps(
                {'start': datetime.now().isoformat(),
                 'end':  datetime.now().isoformat(),
                 'output': 'Sample output',
                 'revision': 'some-revision'}))
        self.assertEqual(self.project.buildlog_set.count(), 1)

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestAPIBase),
            unittest.makeSuite(TestProjectOverview),
            unittest.makeSuite(TestProject),
            ])
