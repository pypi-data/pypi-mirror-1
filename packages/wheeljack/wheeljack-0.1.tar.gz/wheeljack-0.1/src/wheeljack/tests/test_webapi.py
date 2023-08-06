import unittest
from datetime import datetime

from wheeljack.testing import APITestCase

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
             "name": "Bumblebee", "last_revision": "", "repository": ""})

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
            unittest.makeSuite(TestProjectOverview),
            unittest.makeSuite(TestProject),
            ])
