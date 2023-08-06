import unittest
from datetime import datetime

from django.core import mail

from wheeljack.testing import FunctionalTestCase

class TestSendNotificationMail(FunctionalTestCase):

    def test_signal_hookup(self):
        # The people who are subscribed to a project receive a notification
        # when the project fails to build. This is done using a signal that is
        # triggered at the creation of build log entries.
        from django.db.models.signals import post_save
        from wheeljack.notification import mail_build_report

        self.assert_(mail_build_report in
                     [ref() for key, ref in post_save.receivers])

    def test_send_notification(self):
        # The notification is send using the Django mail system. It uses the
        # list of interested parties from the project that is linked to the
        # build report.
        class Manager(object):
            def order_by(self, key):
                return [BuildLog()]

        class Project(object):
            name = 'The Immobilizer'
            watch_list = '''
              optimus.prime@autobots.earth
              perceptor@autobots.earth                               
           '''
            buildlog_set = Manager()

        class BuildLog(object):
            project = Project()
            revision = 'first-rev'
            start = datetime(1985, 9, 24, 18, 00)
            end = datetime(1985, 9, 24, 19, 00)
            state = 'FAILED'
            output = 'Stuff broke.'

        from wheeljack.notification import mail_build_report
        mail_build_report(None, BuildLog())
        # This should have send one mail message
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        # The recipients should match those from the project.
        self.assertEqual(message.to, ['optimus.prime@autobots.earth',
                                      'perceptor@autobots.earth'])
        # The message has an explanation of the failure.
        self.assert_('Stuff broke' in str(message.message()))

    def test_do_not_notify_on_repeated_success(self):
        # Successful builds should not trigger a mail message.
        class Manager(object):
            def order_by(self, key):
                return [BuildLog()]

        class Project(object):
            buildlog_set = Manager()

        class BuildLog(object):
            state = 'OK'
            project = Project()

        from wheeljack.notification import mail_build_report
        mail_build_report(None, BuildLog())
        # This should have send no mail message
        self.assertEqual(len(mail.outbox), 0)

    def test_notify_on_success_after_failure(self):
        # A message should be send when a successful build follows a broken
        # build.
        class Manager(object):
            def order_by(self, key):
                return [BuildLog('FAILED'), BuildLog('OK')]

        class Project(object):
            buildlog_set = Manager()
            name = 'Wheeljack'
            watch_list = '''
              optimus.prime@autobots.earth
              perceptor@autobots.earth                               
           '''

        class BuildLog(object):
            project = Project()
            start = datetime(1985, 9, 24, 18, 00)
            end = datetime(1985, 9, 24, 19, 00)

            def __init__(self, state='OK'):
                self.state = state

        from wheeljack.notification import mail_build_report
        mail_build_report(None, BuildLog())

        self.assertEqual(len(mail.outbox), 1)



def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestSendNotificationMail),
            ])
