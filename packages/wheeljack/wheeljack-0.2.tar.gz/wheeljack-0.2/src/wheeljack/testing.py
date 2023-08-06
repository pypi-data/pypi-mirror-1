import base64

from django.db import transaction
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase as DjangoTestCase
from django.test import Client
from django.core import mail
from django.conf import settings
from django.core.urlresolvers import clear_url_caches
import simplejson as json

class DjangoLayer(object):
    """A test layer for use with zc.testing.

    This sets up a test environment (database connection etc.) just like the
    default Django testrunner would do. The advantage of this layer is that it
    enables the usage of the zc.testing test runner.
    """

    @classmethod
    def setUp(self):
        settings.DEBUG = False
        self.pre_existing_db_name = settings.DATABASE_NAME
        from django.test import utils
        utils.setup_test_environment()
        # Create the database
        self.__old_name = settings.DATABASE_NAME
        from django.db import connection
        connection.creation.create_test_db(verbosity=1,
                                           autoclobber=True)

    @classmethod
    def tearDown(self):
        from django.db import connection
        connection.creation.destroy_test_db(self.__old_name, verbosity=1)
        from django.test import utils
        utils.teardown_test_environment()


class FunctionalTestCase(DjangoTestCase):
    """Extended version of the Django test.

    This makes functional testing faster and easier. It employs tricks like
    using transactions to avoid database setup & teardown to improve speed.
    """

    layer = DjangoLayer

    def _pre_setup(self):
        transaction.enter_transaction_management()
        transaction.managed(True)
        if hasattr(self, 'fixtures'):
            # We have to use this slightly awkward syntax due to the fact
            # that we're using *args and **kwargs together.
            call_command('loaddata', *self.fixtures, **{'verbosity': 0})
        if hasattr(self, 'urls'):
            self._old_root_urlconf = settings.ROOT_URLCONF
            settings.ROOT_URLCONF = self.urls
            clear_url_caches()
        mail.outbox = []

    def _post_teardown(self):
        transaction.rollback()
        super(FunctionalTestCase, self)._post_teardown()


class APIClient(Client):
    """Test client which sends login info as basic auth data."""

    def login(self, username, password):
        """Sets basic authentication headers for any further request."""
        self.defaults['HTTP_AUTHORIZATION'] = 'basic %s' % (
            base64.b64encode('%s:%s' % (username, password)))

    def put(self, *args, **extra):
        """Requests a response from the server using PUT."""
        extra['REQUEST_METHOD'] = 'PUT'
        return self.post(*args, **extra)


class APITestCase(FunctionalTestCase):
    """Base class for testing API views

    Subclasses are expected to setup an url property. This should
    point to the view that will be tested. This class automatically
    checks that this view is secured. It also sets up a default user
    with a profile.
    """

    def setUp(self):
        super(APITestCase, self).setUp()
        # Setup a default user
        self.user = User.objects.create_user(
            'docter', 'thedocter@timelords', 'rose')

        # Subclasses can expect the user to be logged in
        self.client = APIClient()
        self.client.login(username='docter', password='rose')

    def assertEqualJSON(self, response, data):
        """Assert that the response matches the Python data.

        This makes sure that the response has the proper headers. It also
        automatically converts the response body to a parsed structure ready to
        compare with the given data.
        """
        try:
            self.assertEqual(
                json.loads(response.content), data,
                'Response output: %s does not match expected: %s' % (
                    response.content, data))
        except ValueError, e:
            raise AssertionError, 'Invalid JSON: %s' % response.content

    def test_view_is_protected(self):
        # Make sure that the url is protected. Subclasses are expected
        # to set this url.
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'],
                         'Basic realm="Cybertron"')
