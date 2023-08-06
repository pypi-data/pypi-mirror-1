import base64

from django.http import HttpResponse
from django.contrib import auth
from django.http import HttpResponseForbidden

class login_required(object):
    """Checks for a authorized user, sends a HTTP challenge otherwise.
    
    This decorator also checks for basic authentication credentials.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        return login_required(self.func.__get__(obj, cls))

    def __call__(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            if not 'HTTP_AUTHORIZATION' in request.META:
                r = HttpResponse('Basic authentication required',
                                 status=401)
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
        return self.func(request, *args, **kwargs)
