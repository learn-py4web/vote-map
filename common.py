"""
This file defines cache, session, and translator T object for the app
These are fixtures that every app needs so probably you will not be editing this file
"""
import os
from py4web import Session, Cache, Translator, DAL, Field
from py4web.utils.auth import Auth
from py4web.utils.tags import Tags
from py4web.utils.factories import ActionFactory
from py4web.utils.url_signer import URLSigner
from . import settings

if os.environ.get("GAE_ENV"):
    # We are on appengine.
    db = DAL(settings.GAE_DB_URI,
             migrate_enabled=False, # No DB migrations in production.
             pool_size=settings.DB_POOL_SIZE)
else:
    # We are on localhost.
    db = DAL(settings.TESTING_DB_URI,
             folder=settings.DB_FOLDER,
             pool_size=settings.DB_POOL_SIZE)

# define global objects that may or may not be used by th actions
cache = Cache(size=1000)
T = Translator(settings.T_FOLDER)

# pick the session type that suits you best
if settings.SESSION_TYPE == 'cookies':
    session = Session(secret=settings.SESSION_SECRET_KEY)
elif settings.SESSION_TYPE == 'redis':
    import redis
    host, port = settings.REDIS_SERVER.split(':')
    # for more options: https://github.com/andymccurdy/redis-py/blob/master/redis/client.py
    conn = redis.Redis(host=host, port=int(port))
    conn.set = lambda k, v, e, cs=conn.set, ct=conn.ttl: (cs(k, v), e and ct(e))
    session = Session(secret=settings.SESSION_SECRET_KEY, storage=conn)
elif settings.SESSION_TYPE == 'memcache':
    import memcache, time
    conn = memcache.Client(settings.MEMCACHE_CLIENTS, debug=0)
    session = Session(secret=settings.SESSION_SECRET_KEY, storage=conn)
elif settings.SESSION_TYPE == 'database':
    from py4web.utils.dbstore import DBStore
    session =  Session(secret=settings.SESSION_SECRET_KEY, storage=DBStore(db))

auth = Auth(session, db,
            registration_requires_confirmation=False,
            password_complexity=False,
            use_username=True)

if auth.db:
    groups = Tags(db.auth_user, 'groups')

if settings.USE_PAM:
    from py4web.utils.auth_plugins.pam_plugin import PamPlugin
    auth.register_plugin(PamPlugin())

if settings.USE_LDAP:
    from py4web.utils.auth_plugins.ldap_plugin import LDAPPlugin
    auth.register_plugin(LDAPPlugin(**settings.LDAP_SETTINGS))

if settings.OAUTH2GOOGLE_CLIENT_ID:
    from py4web.utils.auth_plugins.oauth2google import OAuth2Google # TESTED
    auth.register_plugin(OAuth2Google(client_id=settings.OAUTH2GOOGLE_CLIENT_ID,
                                      client_secret=settings.OAUTH2GOOGLE_CLIENT_SECRET,
                                      callback_url='auth/plugin/oauth2google/callback'))

auth.enable()

unauthenticated = ActionFactory(db, session, T, auth)
authenticated = ActionFactory(db, session, T, auth.user)

signed_url = URLSigner(session)
