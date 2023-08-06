from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.exceptions import ObjectDoesNotExist

from wheeljack import models

class BuildLogEntries(Feed):
    feed_type = Atom1Feed

    def get_object(self, args):
        """Return the project object."""
        if len(args) != 1:
            raise ObjectDoesNotExist
        return models.Project.objects.get(pk=args[0])

    def title(self, obj):
        """Feed title."""
        return obj.name

    def link(self, obj):
        """Link pointing to the project info page."""
        return obj.get_absolute_url()

    def items(self, obj):
        """Return the latest build log entries."""
        return obj.buildlog_set.order_by('-id')[:5]

    def item_pubdate(self, item):
        """Return the entries start date."""
        return item.start
