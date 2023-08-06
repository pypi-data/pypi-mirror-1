from django.db import models

from wheeljack.repositories import supported_repositories

class Project(models.Model):
    name = models.CharField(max_length=256)
    build_cmd = models.CharField(max_length=256)
    repository = models.CharField(max_length=256)
    vcs = models.CharField(max_length=8, choices=supported_repositories)
    watch_list = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)

    @property
    def require_build(self):
        """If a build operation is required regardless of updates."""
        build = self.last_build
        if build is None:
            return True
        if self.last_modified > build.start:
            return True
        return False

    @property
    def last_build(self):
        log_entries = self.buildlog_set.order_by('end').reverse()
        try:
            return log_entries[0]
        except IndexError:
            return None

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', [str(self.id)])

states = (('FAILURE', 'FAILURE'), ('SUCCESS', 'SUCCESS'),
          ('BUILDING', 'BUILDING'))

class BuildLog(models.Model):
    project = models.ForeignKey(Project)
    revision = models.CharField(max_length=512)
    output = models.TextField()
    state = models.CharField(max_length=32, choices=states)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return '%s (%s)' % (self.state, self.start.strftime('%x %X'))

    @models.permalink
    def get_absolute_url(self):
        return ('wheeljack.views.project_detail', [self.project.id, self.id])
