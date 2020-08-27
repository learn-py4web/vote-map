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
    Field('lat', 'double'),
    Field('lng', 'double'),
    Field('address_lat', 'double'),
    Field('address_lng', 'double'),
    Field('square10'),
    Field('name'),
    Field('loc_type'),
    Field('type_other'),
    Field('county'),
    Field('address', 'text'),
    Field('rules', 'text'),
    Field('notes', 'text'),
    Field('date_created', 'datetime', default=get_time),
    Field('date_updated', 'datetime', update=get_time),
)

# These are also given to the webapp.
LOCATION_FIELDS = [
    'id', 'is_deleted', 'lat', 'lng', 'address_lat', 'address_lng',
    'name', 'loc_type', 'type_other', 'county',
    'address', 'rules', 'notes',
]


db.define_table(
    'location_history',
    Field('is_deleted', 'boolean'),
    Field('author', default=get_user_email),
    Field('location_id', 'reference location', ondelete="NO ACTION"),
    Field('lat', 'double'),
    Field('lng', 'double'),
    Field('address_lat', 'double'),
    Field('address_lng', 'double'),
    Field('square10'),
    Field('name'),
    Field('loc_type'),
    Field('type_other'),
    Field('county'),
    Field('address', 'text'),
    Field('rules', 'text'),
    Field('notes', 'text'),
    Field('max_zoom', 'integer'), # Max zoom level used in edit.
    Field('edit_time', 'integer'), # How long did the edit last.
    Field('timestamp', 'datetime', default=get_time),
)


db.define_table(
    'vote',
    Field('location_history_id', 'reference location_history'),
    Field('author', default=get_user_email),
    Field('timestamp', 'datetime', default=get_time),
    Field('max_zoom', 'integer'), # Max zoom level used to confirm.
)


db.define_table(
    'zipcode',
    Field('zipcode'),
    Field('lat', 'double'),
    Field('lng', 'double'),
)


db.define_table(
    'userinfo',
    Field('email', default=get_user_email),
    Field('can_edit', 'boolean'),
    Field('can_invite', 'boolean'),
    Field('invited_by'),
    Field('invitation_code'),
    Field('created_date', 'datetime', default=get_time),
    Field('updated_date', 'datetime', update=get_time),
)


db.commit()
