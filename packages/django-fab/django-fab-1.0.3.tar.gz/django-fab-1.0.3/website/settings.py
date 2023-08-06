import os
from os.path import dirname
import pinax

try:
    DEBUG
except NameError:
    DEBUG = True

#test change
PLATFORM_ROOT = os.path.realpath(dirname(dirname(dirname(dirname(pinax.__file__)))))
PROJECT_ROOT = os.path.realpath(dirname(__file__))
execfile(PLATFORM_ROOT + '/core_website/website_settings.py')

DATABASE_ENGINE = 'mysql'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'aurealty'       # Or path to database file if using sqlite3.
DATABASE_USER = 'lifeuser'             # Not used with sqlite3.
DATABASE_PASSWORD = '8uhbnji'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


execfile(PLATFORM_ROOT + '/core_website/core_settings.py')
execfile(PLATFORM_ROOT + '/core_website/satchmo_settings.py')

#INSTALLED_APPS += (
#'subscriptiontribes',
#)


#PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media")


