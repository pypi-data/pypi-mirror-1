from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib.syndication.views import feed

from wheeljack import models
from wheeljack.feeds import BuildLogEntries
from wheeljack.decorators import login_required
# Import for side effects of registering signals.
from wheeljack import notification
notification # Pyflakes


generic_view_patterns = patterns(
    'django.views.generic',
    url(r'^project/add/$', 'create_update.create_object',
        {'model': models.Project, 'login_required': True}, name='add_project'),
    url(r'^project/(?P<object_id>\d+)/edit$', 'create_update.update_object',
        {'model': models.Project, 'login_required': True},
        name='edit_project'),
    url(r'^project/(?P<object_id>\d+)/delete$', 'create_update.delete_object',
        {'model': models.Project, 'login_required': True,
         'post_delete_redirect': '/'}, name='delete_project'),
)

view_patterns = patterns(
    'wheeljack.views',    url(r'^$', 'project_list', name='project_overview'),
    url(r'^project/(\d+)/log/(\d+)/$', 'project_detail'),
    url(r'^project/(\d+)/$', 'project_detail', name='project_detail'),
)

api_patterns = patterns(
    'wheeljack.views',
    (r'^api/project/(\d+)/log/(\d+)/', 'buildlog_api'),
    (r'^api/project/(\d+)/', 'project_api'),
    (r'^api/', 'project_overview_api'),
)

feeds = {'buildlog': BuildLogEntries}

feed_patterns = patterns(
    '',
    url(r'^feeds/(?P<url>.*)/$', login_required(feed), {'feed_dict': feeds},
        name='feeds'))

urlpatterns = (generic_view_patterns + view_patterns + api_patterns +
               feed_patterns)
