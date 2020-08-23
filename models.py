"""
This file defines the database models
"""
import datetime

from . common import db, Field, auth
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'location',
    Field('is_deleted', 'boolean', default=False),
    Field('author', default=get_user_email),
    Field('lat', 'double'),
    Field('lng', 'double'),
    Field('address_lat', 'double'),
    Field('address_lng', 'double'),
    Field('name'),
    Field('loc_type'),
    Field('type_other'),
    Field('date_open', 'date'),
    Field('date_close', 'date'),
    Field('time_open', 'time'),
    Field('time_close', 'time'),
    Field('address'),
    Field('rules', 'text'),
    Field('date_created', 'datetime', default=get_time),
    Field('date_updated', 'datetime', update=get_time),
)


db.define_table(
    'location_history',
    Field('is_deleted', 'boolean'),
    Field('author', default=get_user_email),
    Field('location_id', 'reference location', ondelete="NO ACTION"),
    Field('lat', 'double'),
    Field('lng', 'double'),
    Field('address_lat', 'double'),
    Field('address_lng', 'double'),
    Field('name'),
    Field('loc_type'),
    Field('type_other'),
    Field('date_open', 'date'),
    Field('date_close', 'date'),
    Field('time_open', 'time'),
    Field('time_close', 'time'),
    Field('address'),
    Field('rules', 'text'),
    Field('timestamp', 'datetime', default=get_time),
)


db.define_table(
    'vote',
    Field('location_history_id', 'reference location_history'),
    Field('author', default=get_user_email),
    Field('timestamp', 'datetime', default=get_time),
)


db.commit()
