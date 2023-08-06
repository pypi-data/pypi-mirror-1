from django.db.models import signals
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from wheeljack import models

def mail_build_report(sender, instance=None, **kwargs):
    """Send a build report to interested parties in case of errors."""
    # Only notify in case of errors
    if instance.success:
       return

    project = instance.project

    context = Context({'project': project, 'buildlog': instance})
    message = get_template('wheeljack/mail_build_report.txt').render(context)

    send_mail(u'[Build error] %s' % project.name,
              message, settings.DEFAULT_FROM_EMAIL,
              recipient_list=project.watch_list.split())

signals.post_save.connect(mail_build_report, sender=models.BuildLog)
