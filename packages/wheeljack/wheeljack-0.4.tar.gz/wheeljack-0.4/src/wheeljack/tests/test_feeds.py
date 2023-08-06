import unittest

import mock

class TestBuildLogFeed(unittest.TestCase):

    @property
    def feed(self):
        from wheeljack.feeds import BuildLogEntries
        return BuildLogEntries

    @mock.patch('wheeljack.models.Project')
    def test_get_object(self, project):
        # The feed is specific for a certain project.
        feed = self.feed(None, mock.Mock())
        feed.get_object([1])
        project.objects.get.assert_called_with(pk=1)

    @mock.patch('wheeljack.models.Project')
    def test_get_object_without_project_id(self, project):
        # When given to little arguments (no project id) the get_object method
        # will raise an error.
        feed = self.feed(None, mock.Mock())
        from django.core.exceptions import ObjectDoesNotExist
        self.assertRaises(ObjectDoesNotExist, feed.get_object, [])

    def test_title(self):
        # The title method return the name of the project.
        feed = self.feed(None, mock.Mock())
        project = mock.Mock()
        project.name = 'Cybertron'
        self.assertEqual(feed.title(project), 'Cybertron')

    def test_link(self):
        # The feed link points to the project's URL.
        feed = self.feed(None, mock.Mock())
        project = mock.Mock()
        project.get_absolute_url.return_value = 'http://earth/cybertron'
        self.assertEqual(feed.link(project), 'http://earth/cybertron')

    def test_items(self):
        # A selection of the most recent build log entries form the items of
        # the feed.
        feed = self.feed(None, mock.Mock())
        project = mock.Mock()
        project.buildlog_set.order_by.return_value = []
        feed.items(project)
        project.buildlog_set.order_by.assert_called_with('-id')

    def test_item_pubdate(self):
        # The publication date of each item is based on it's start date.
        item = mock.Mock()
        item.start = 'now'
        feed = self.feed(None, mock.Mock())
        self.assertEqual(feed.item_pubdate(item), 'now')

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestBuildLogFeed),
            ])
