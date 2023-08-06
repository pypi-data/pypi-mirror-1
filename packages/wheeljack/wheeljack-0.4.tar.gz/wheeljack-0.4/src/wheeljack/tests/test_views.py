import unittest
from datetime import datetime

import mock

from wheeljack.testing import FunctionalTestCase

class TestProjectDetail(FunctionalTestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        # Setup a default user
        self.user = User.objects.create_user(
            'wheeljack', 'wheeljack@earth', 'cybertron')
        self.client.login(username='wheeljack', password='cybertron')

    @mock.patch('subprocess.Popen')
    def test_force_build(self, Popen):
        # The build can be forced by posting to this view.
        from wheeljack.models import Project
        project = Project.objects.create(name='Grimlock')
        response = self.client.post('/project/1/')
        self.assertRedirects(response, '/project/1/')
        # In the mean time the Popen object should have been instantiated.
        from django.conf import settings
        Popen.assert_called_with(
            [settings.BUILDER, 'build',
             '--settings=wheeljack.project.development',
             u'http://testserver/api/project/1/'],
            close_fds=True)

    def test_display_build_state(self):
        # The current build state should be visible from the detail page.
        from wheeljack.models import Project
        project = Project.objects.create(name='Grimlock')
        # This project does not have any builds yet.
        self.assert_('OK' not in self.client.get('/project/1/').content)
        # Creating a log entry with a different state should show that state.
        project.buildlog_set.create(state='OK', start=datetime.now(),
                                    end=datetime.now())
        self.assert_('OK' in self.client.get('/project/1/').content)


def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestProjectDetail)
            ])
