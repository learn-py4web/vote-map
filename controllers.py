"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url
from . settings_private import MAPS_API_KEY
from .test_data import TEST_LOCATIONS
from .constants import MAX_MAP_RESULTS
from .util import cleanup

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', url_signer)
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        callback_url = URL('callback', signer=url_signer),
        MAPS_API_KEY = MAPS_API_KEY
    )

@action('edit')
@action.uses('edit.html', url_signer, auth.user)
def edit():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        callback_url = URL('edit_callback', signer=url_signer),
        MAPS_API_KEY = MAPS_API_KEY
    )


@action('edit_callback', method='GET')
@action.uses(url_signer.verify())
def edit_callback():
    lat_max = float(request.params.get('lat_max'))
    lat_min = float(request.params.get('lat_min'))
    lng_max = float(request.params.get('lng_max'))
    lng_min = float(request.params.get('lng_min'))
    print(lat_min, lat_max, lng_min, lng_max)
    q = ((db.location.lat >= lat_min) & (db.location.lat <= lat_max) &
         (db.location.lng >= lng_min) & (db.location.lng <= lng_max))
    ql = q & (db.location.is_deleted == True)
    qd = q & (db.location.is_deleted == False)
    may_be_incomplete = False
    live_results = db(ql).select(limitby=(0, MAX_MAP_RESULTS)).as_list()
    dead_results = []
    if len(live_results) == MAX_MAP_RESULTS:
        may_be_incomplete = True
    elif request.params.get('include_deleted'):
        dead_results = db(qd).select(limitby=(0, MAX_MAP_RESULTS - len(live_results))).as_list()
        may_be_incomplete = len(live_results) + len(dead_results) == MAX_MAP_RESULTS
    return dict(
        locations=live_results + dead_results,
        may_be_incomplete=may_be_incomplete,
    )


@action('edit_callback', method='POST')
@action.uses(url_signer.verify())
def post_edit():
    """Stores an edit, returning the ID if any."""
    print(request.params)
    d = {}
    id = request.params.get('id')
    if d.get('is_vote'):
        # This is a vote.
        register_vote(id)
        return "ok"
    d['is_deleted'] = request.params.get('is_deleted')
    d['lat'] = request.params.get('lat')
    d['lng'] = request.params.get('lng')
    d['address_lat'] = request.params.get('address_lat')
    d['address_lng'] = request.params.get('address_lng')
    d['name'] = request.params.get('name')
    d['loc_type'] = request.params.get('loc_type')
    d['type_other'] = request.params.get('type_other')
    d['date_open'] = request.params.get('date_open')
    d['date_close'] = request.params.get('date_close')
    d['time_open'] = request.params.get('time_open')
    d['time_close'] = request.params.get('time_close')
    d['address'] = request.params.get('address')
    d['rules'] = request.params.get('rules')
    new_id = perform_update(id, d)
    return dict(new_id=new_id)


def register_vote(id):
    """Registers a vote in favor of a location."""
    # Determines the location history id.
    loc_hist = db(db.loaction_history.location_id == id).select(orderby=~db.location_history.timestamp).first()
    if loc_hist is None:
        return
    db.vote.update_or_insert(
        (db.location_history_id == loc_hist.id),
        location_history_id=loc_hist.id
    )


def perform_update(id, d):
    """Performs the update corresponding to dictionary d, noting the
    outcome in the location history."""
    if id is not None:
        # Update.
        cleanup(d, ['id', 'author'])
        db(db.location.id == id).update(**d)
        d['location_id'] = id
        new_id = None
    else:
        # Insert.
        cleanup(d, ['id', 'author'])
        new_id = db.location.insert(**d)
        d['location_id'] = new_id
    # Updates the history.
    db.location_history.insert(**d)
    return new_id


# TODO: add mechanism to vote on items

# TODO: remove this testing code.

@action('initdb')
@action.uses(auth.user)
def initdb():
    cleardb()
    for d in TEST_LOCATIONS:
        perform_update(None, d)
    return "ok"

@action('cleardb')
@action.uses(auth.user)
def cleardb():
    db(db.location).delete()
    db(db.location_history).delete()
    db(db.vote).delete()

###############################################
# Old below

@action('refine')
@action.uses('refine.html', url_signer)
def refine():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        callback_url = URL('callback', signer=url_signer),
        MAPS_API_KEY = MAPS_API_KEY
    )

@action('staticmap')
@action.uses('staticmap.html', url_signer)
def staticmap():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        callback_url = URL('callback', signer=url_signer),
    )

@action('embedmap')
@action.uses('embedmap.html', url_signer)
def embedmap():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        callback_url = URL('callback', signer=url_signer),
        MAPS_API_KEY = MAPS_API_KEY
    )

