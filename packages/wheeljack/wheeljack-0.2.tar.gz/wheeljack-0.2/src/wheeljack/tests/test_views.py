import unittest

from wheeljack.testing import FunctionalTestCase

class TestProjectDetail(FunctionalTestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        # Setup a default user
        self.user = User.objects.create_user(
            'wheeljack', 'wheeljack@earth', 'cybertron')
        self.client.login(username='wheeljack', password='cybertron')

    def test_force_build(self):
        # The build can be forced by posting to this view.
        from wheeljack.models import Project
        project = Project.objects.create(name='Grimlock')
        response = self.client.post('/project/1/')
        self.assertRedirects(response, '/project/1/')

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestProjectDetail)
            ])
