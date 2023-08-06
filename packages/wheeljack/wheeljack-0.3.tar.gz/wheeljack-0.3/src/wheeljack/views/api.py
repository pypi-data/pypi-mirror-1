import base64

import simplejson as json
import dateutil.parser

from django.contrib import auth
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.utils.timesince import timesince

from wheeljack import models

class API(object):
    """Base class for API views.

    This class forms the base for all API views. It has a __call__ that enables
    basic authentication, calls a handler based on the method and converts
    return values to a proper JSON response.
    """

    def __call__(self, request, *args, **kwargs):
        """ Execute the appropriate view action."""
        if not request.user.is_authenticated():
            if not 'HTTP_AUTHORIZATION' in request.META:
                r = HttpResponse('Basic authentication required', status=401)
                r['WWW-Authenticate'] = 'Basic realm="Cybertron"'
                return r

            authentication = request.META['HTTP_AUTHORIZATION'].split()
            if len(authentication) != 2 or (
                authentication[0].lower() != "basic"):
                return HttpResponseForbidden(
                    'Only basic authentication is supported')

            uname, passwd = base64.b64decode(authentication[1]).split(':')
            user = auth.authenticate(username=uname, password=passwd)
            if user is None or not user.is_active:
                return HttpResponseForbidden('Invalid user or password')

            auth.login(request, user)
            request.user = user

        method = request.method.lower()
        allowed_methods = [m for m in ('get', 'put', 'post', 'delete')
                           if getattr(self, m, None)]
        if method not in allowed_methods:
            return HttpResponseNotAllowed(allowed_methods)

        handler = getattr(self, method)
        data = handler(request, *args, **kwargs)
        return HttpResponse(json.dumps(data))


class ProjectOverview(API):

    def get(self, request):
        return {'projects': [
                {'name': p.name,
                 'href': request.build_absolute_uri(
                        reverse('wheeljack.views.project_api', args=[p.pk]))}
                for p in models.Project.objects.all()]}

project_overview = ProjectOverview()

class Project(API):

    def get(self, request, pk):
        project = models.Project.objects.get(pk=pk)
        last_build = project.last_build
        if last_build is not None:
            last_revision = last_build.revision
        else:
            last_revision = ''

        data = {'url': request.build_absolute_uri(reverse(
                    'wheeljack.views.project_api', args=[project.pk])),
                'name': project.name,
                'build_cmd': project.build_cmd,
                'repository': project.repository,
                'vcs': project.vcs,
                'require_build': project.require_build,
                'last_revision': last_revision}
        return data

    def post(self, request, pk):
        project = models.Project.objects.get(pk=pk)
        data = json.loads(request.raw_post_data)
        data['start'] = dateutil.parser.parse(data['start'])
        data['end'] = dateutil.parser.parse(data['end'])
        kwargs = dict([(str(key), value) for key, value in data.iteritems()])
        buildlog = project.buildlog_set.create(**kwargs)
        return {'url': request.build_absolute_uri(reverse(
                    'wheeljack.views.buildlog_api',
                    args=[project.pk, buildlog.pk]))}

project = Project()


class BuildLog(API):

    def put(self, request, project_pk, log_pk):
        buildlog = models.BuildLog.objects.get(pk=log_pk)
        data = json.loads(request.raw_post_data)
        data['start'] = dateutil.parser.parse(data['start'])
        data['end'] = dateutil.parser.parse(data['end'])
        for key in ('start', 'end', 'output', 'state', 'revision'):
            setattr(buildlog, key, data[key])
        buildlog.save()
        return {'url': ''}

    def get(self, request, project_pk, log_pk):
        buildlog = models.BuildLog.objects.get(pk=log_pk)
        return {'output': buildlog.output,
                'state': buildlog.state,
                'start': buildlog.start.isoformat(),
                'end': buildlog.end.isoformat(),
                'buildtime': timesince(buildlog.start, buildlog.end)}

buildlog = BuildLog()
