from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=256)
    build_cmd = models.CharField(max_length=256)
    repository = models.CharField(max_length=256)
    watch_list = models.TextField()

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

class BuildLog(models.Model):
    project = models.ForeignKey(Project)
    revision = models.CharField(max_length=512)
    output = models.TextField()
    success = models.BooleanField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        if self.success:
            state = 'OK'
        else:
            state = 'FAILED'
        return '%s (%s)' % (state, self.start.strftime('%x %X'))
