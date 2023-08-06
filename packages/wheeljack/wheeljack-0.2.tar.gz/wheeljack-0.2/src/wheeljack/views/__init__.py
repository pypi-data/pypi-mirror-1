from datetime import datetime
from datetime import timedelta

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from wheeljack.views.api import project as project_api
from wheeljack.views.api import project_overview as project_overview_api
from wheeljack import models

# Pyflakes
project_api
project_overview_api

@login_required
def project_list(request):
    queryset = models.Project.objects.order_by('name').distinct()

    if 'q' in request.GET:
        q = request.GET['q']
        queryset = queryset.filter(
            Q(buildlog__output__icontains=q) | Q(name__icontains=q))

    for key, value in request.GET.iteritems():
        if key == 'q':
            continue
        qf = {str(key): value}
        queryset = queryset.filter(**qf)

    def create_filter_item(name, fieldname, **filters):
        item = {'display': name}
        query = request.GET.copy()
        for key in list(query.iterkeys()):
            if key.startswith(fieldname):
                del query[key]
        for key, value in filters.iteritems():
            query['%s__%s' % (fieldname, key)] = value
        item['query_string'] = '?' + query.urlencode()
        item['selected'] = not set(query.iteritems()).symmetric_difference(
            set(request.GET.iteritems()))
        return item

    date_filter = []
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    for name, filters in (
        ('All', {}), ('Today', {'day': str(now.day),
                                'month': str(now.month),
                                'year': str(now.year)}),
        ('Past 7 days', {'lte': now.strftime('%Y-%m-%d 23:59'),
                         'gte': week_ago.strftime('%Y-%m-%d')}),
        ('This month', {'month': str(now.month), 'year': str(now.year)})):
        date_filter.append(
            create_filter_item(name, 'buildlog__start', **filters))

    state_filter = []
    for name, filters in (('All', {}), ('OK', {'exact': '1'}),
                          ('FAILED', {'exact': '0'})):
        state_filter.append(
            create_filter_item(name, 'buildlog__success', **filters))

    return object_list(
        request,
        extra_context={'date_filter': date_filter,
                       'state_filter': state_filter},
        queryset=queryset)

@login_required
def project_detail(request, object_id, buildlog=None):
    project = get_object_or_404(models.Project, pk=object_id)

    if request.method == 'POST':
        # This indicates a request to force the build. All we need to do is
        # update the modification time of the project.
        project.save()
        return HttpResponseRedirect('/project/%s/' % project.pk)

    if buildlog is None:
        buildlog = project.last_build
    else:
        buildlog = get_object_or_404(models.BuildLog, pk=buildlog)

    return render_to_response(
        'wheeljack/project_detail.html',
        RequestContext(request, {'object': project,
                                 'buildlog': buildlog}))


