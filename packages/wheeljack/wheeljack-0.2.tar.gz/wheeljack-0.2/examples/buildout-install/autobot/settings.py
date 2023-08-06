from wheeljack.project.settings import *

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

EMAIL_HOST='localhost'
DEFAULT_FROM_EMAIL='info@localhost'

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.path.join(
    os.path.split(os.path.dirname(__file__))[0], 'var', 'wheeljack.db')
DATABASE_USER = '' # Not used with sqlite3.
DATABASE_PASSWORD = '' # Not used with sqlite3.
DATABASE_HOST = '' # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '' # Set to empty string for default. Not used with sqlite3.

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

# Don't share this with anybody.
SECRET_KEY = '9u+m8je7gvpdoc@iu^xv%+g68kopa-a(zyb5lw7z*j^jzm+d+!'

DEBUG = True


