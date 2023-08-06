from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from wheeljack.models import Project
from wheeljack.models import BuildLog

site = admin.sites.AdminSite()

# Hookup the default user system
site.register(User, UserAdmin)
site.register(Group, GroupAdmin)


class BuildLogInline(admin.StackedInline):
    model = BuildLog

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ('name', 'repository')
    list_display = ('name', 'build_state', 'build_date', 'repository')
    inlines = [BuildLogInline]

    def build_state(self, obj):
        last_build = obj.last_build
        if last_build is not None:
            return last_build.success
        return False
    build_state.boolean = True

    def build_date(self, obj):
        last_build = obj.last_build
        if last_build is not None:
            return last_build.start

site.register(Project, ProjectAdmin)

class BuildLogAdmin(admin.ModelAdmin):
    search_fields = ('output',)
    list_display = ('project', 'start', 'end', 'success')
    list_filter = ('project', 'start', 'success')

site.register(BuildLog, BuildLogAdmin)
