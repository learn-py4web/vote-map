"""
This is an optional file that defined app level settings such as:
- database settings
- session settings
- i18n settings
This file is provided as an example:
"""
import os

# try import private settings
try: from . settings_private import *
except: pass

# db settings
APP_FOLDER = os.path.dirname(__file__)
# DB_FOLDER:    Sets the place where migration files will be created
#               and is the store location for SQLite databases
DB_FOLDER = os.path.join(APP_FOLDER, 'databases')
DB_POOL_SIZE = 1

TESTING_DB_URI = "sqlite://storage.db"

# This is the URL of MySQL as accessed from Google Appengine
GAE_DB_URI = "google:MySQLdb://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{DB_CONNECTION}".format(
    DB_USER=DB_USER,
    DB_NAME=DB_NAME,
    DB_PASSWORD=DB_PASSWORD,
    DB_CONNECTION=DB_CONNECTION
)

# session settings
SESSION_TYPE = 'database'
SESSION_SECRET_KEY = '<my secret key>'
MEMCACHE_CLIENTS = ['127.0.0.1:11211']
REDIS_SERVER = 'localhost:6379'

# enable PAM
USE_PAM = False

# enable LDAP
USE_LDAP = False
LDAP_SETTING = {
    'mode': 'ad',
    'server': 'my.domain.controller',
    'base_dn': 'ou=Users,dc=domain,dc=com'}

# i18n settings
T_FOLDER = os.path.join(APP_FOLDER, 'translations')

