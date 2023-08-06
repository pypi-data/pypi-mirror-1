import unittest
from datetime import datetime

from wheeljack.testing import FunctionalTestCase

class TestProject(FunctionalTestCase):

    def test_unicode(self):
        # Project's have a nice unicode representation. This is used for the
        # admin etc.
        from wheeljack import models
        project = models.Project.objects.create(name='Geothermal Generator')
        self.assertEqual(unicode(project), u'Geothermal Generator')

    def test_get_absolute_url(self):
        # To make it easier to get links to the project it provides an method.
        from wheeljack import models
        project = models.Project.objects.create(name='Geothermal Generator')
        self.assertEqual(project.get_absolute_url(), '/project/1/')

    def test_require_build(self):
        # The project can indicate that a build is required regardless of
        # updates to the source code. This is automatically triggered for new
        # projects without builds.
        from wheeljack import models
        project = models.Project.objects.create(name='Geothermal Generator')
        self.assert_(project.require_build)
        # Creating a log entry should invalidate the requirement.
        project.buildlog_set.create(start=datetime.now(), end=datetime.now())
        self.failIf(project.require_build)
        # When the project's last modified attribute contains a time later than
        # that of the last build log it will require a new build.
        project.save() # Update the last modified (auto_now)
        self.assert_(project.require_build)


class TestBuildLog(FunctionalTestCase):

    def test_unicode(self):
        # Build log's have a nice unicode representation. This is used for the
        # admin etc.
        from wheeljack import models
        project = models.Project.objects.create(name='Geothermal Generator')
        buildlog = models.BuildLog.objects.create(
            project=project, state='OK', start=datetime(1985, 10, 21),
            end=datetime(1985, 10, 22))
        self.assertEqual(unicode(buildlog), u'OK (10/21/85 00:00:00)')
        # When a build has failed the indication within it's unicode
        # representation will change as well.
        buildlog.state = 'FAILED'
        self.assertEqual(unicode(buildlog), u'FAILED (10/21/85 00:00:00)')


def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestProject),
            unittest.makeSuite(TestBuildLog),
            ])
