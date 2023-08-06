from django.conf.urls.defaults import patterns, handler500
from django.conf.urls.defaults import include
from django.conf.urls.defaults import url
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail


from wheeljack import forms

handler500 # Pyflakes

urlpatterns = patterns(
    '',
    (r'', include('wheeljack.urls')),
)

# User management
urlpatterns += patterns(
    'django.views.generic',
    url(r'^users/$', login_required(list_detail.object_list),
        {'queryset': auth_models.User.objects.all(),
         'template_name': 'wheeljack/user_list.html'},
        name='manage_users'),
    url(r'^users/add/$', 'create_update.create_object',
        {'model': auth_models.User,
         'template_name': 'wheeljack/user_form.html',
         'login_required': True,
         'form_class': forms.UserCreationForm}, name='add_user'),
    url(r'^users/(?P<slug>\w+)/change-password/$', 'create_update.update_object',
        {'model': auth_models.User, 'slug_field': 'username',
         'template_name': 'wheeljack/user_form.html', 'login_required': True,
         'form_class': forms.SetPasswordForm}, name='change_password'),
    url(r'^users/(?P<slug>\w+)/delete$', 'create_update.delete_object',
        {'model': auth_models.User, 'slug_field': 'username',
         'template_name': 'wheeljack/user_confirm_delete.html',
         'login_required': True,
         'post_delete_redirect': '/users/'},
        name='delete_user'),
    url(r'^users/(?P<slug>\w+)/$', 'create_update.update_object',
        {'model': auth_models.User, 'slug_field': 'username',
         'template_name': 'wheeljack/user_form.html', 'login_required': True,
         'form_class': forms.UserForm}),
    )

# Authentication setup
urlpatterns += patterns(
    'django.contrib.auth.views',
    (r'^logout/$', 'logout'),
    (r'^accounts/login/$', 'login'),
    (r'^password_change/$', 'password_change'),
    (r'^password_change_done/$', 'password_change_done'),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
