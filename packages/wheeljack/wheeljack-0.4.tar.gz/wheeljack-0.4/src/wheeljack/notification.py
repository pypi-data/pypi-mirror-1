from django.db.models import signals
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from wheeljack import models

def mail_build_report(sender, instance=None, **kwargs):
    """Send a build report to interested parties in case of errors.

    This will also send a report in case the build has started to work again
    after one or more broken builds. Successful builds after that will not
    trigger a notification."""

    project = instance.project
    buildlogs = project.buildlog_set.order_by('-id')[:2]

    # Only send a report when the state is OK if the one before that was not
    # OK.
    if instance.state == 'OK':
        if len(buildlogs) < 2 or buildlogs[0].state == 'OK':
            return
    # Else only send reports when the state is failed.
    elif instance.state != 'FAILED':
       return

    project = instance.project

    context = Context({'project': project, 'buildlog': instance})
    message = get_template('wheeljack/mail_build_report.txt').render(context)

    send_mail(u'[Build error] %s' % project.name,
              message, settings.DEFAULT_FROM_EMAIL,
              recipient_list=project.watch_list.split())

signals.post_save.connect(mail_build_report, sender=models.BuildLog)
