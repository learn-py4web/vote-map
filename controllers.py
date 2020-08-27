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

import requests
import uuid
import time

from py4web import action, request, abort, redirect, URL, Field, HTTP
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url
from . models import LOCATION_FIELDS, get_user_email
from . settings_private import MAPS_API_KEY, GEOLOCATION_KEY
from .test_data import TEST_LOCATIONS
from .constants import *
from .util import generate_invitation_code, cleanup, latlng_to_square10, get_results_in_region, get_concentric_results

url_signer = URLSigner(session)

### PAGES


@action('index')
@action.uses(auth, 'index.html', url_signer)
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        get_locations_url = URL('get_locations', signer=url_signer),
        MAPS_API_KEY = MAPS_API_KEY
    )


@action('edit')
@action.uses(auth.user, 'edit.html', url_signer)
def edit():
    # Checks if the user can edit.
    r = db(db.userinfo.email == get_user_email()).select().first()
    return dict(
        can_edit = False if r is None else r.can_edit,
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        geolocation_url = URL('geolocation', signer=url_signer),
        callback_url = URL('edit_callback', signer=url_signer),
        MAPS_API_KEY = MAPS_API_KEY
    )


@action('invite')
@action.uses(db, auth.user, 'invite.html', url_signer)
def invite():
    # Checks if the user can edit and/or invite.
    invalid = request.params.get('invalid')
    reason = request.params.get('reason')
    r = db(db.userinfo.email == get_user_email()).select().first()
    if r is not None and r.can_edit and r.can_invite:
        invitation_code = r.invitation_code
    else:
        invitation_code = None
    return dict(
        invalid = invalid,
        reason = reason,
        can_edit = r is not None and r.can_edit,
        can_invite = r is not None and r.can_invite,
        invitation_code = invitation_code,
        validate_url = URL('validate_code'),
        refresh_url = URL('refresh_code', signer=url_signer),
    )


@action('validate_code')
@action.uses(db, auth.user)
def validate_code():
    """Checks whether the invitation is valid, and if so, grants permissions."""
    code = request.params.get('code')
    if code is None:
        redirect(URL('invite', vars=dict(invalid=True, reason="Invalid invitation")))
    # Checks not invited already.
    r = db(db.userinfo.email == get_user_email()).select().first()
    if r is not None:
        redirect(URL('invite', vars=dict(invalid=True, reason="You have already been invited")))
    # Looks up the code.
    inviter = db(db.userinfo.invitation_code == code).select().first()
    if inviter is None or not inviter.can_invite:
        redirect(URL('invite', vars=dict(invalid=True, reason="Invalid invitation")))
    # The invitation is valid.
    # Creates a new code, to invite in turn.
    invitation_code = generate_invitation_code()
    # Writes the record.
    db.userinfo.insert(
        can_edit=True,
        can_invite=True,
        invited_by=inviter.email,
        invitation_code=invitation_code,
    )
    redirect(URL('invite', vars=dict(reason="You can now edit the site")))


@action('refresh_code')
@action.uses(db, auth.user, url_signer.verify())
def refresh_code():
    r = db(db.userinfo.email == get_user_email()).select().first()
    if r is None or not r.can_invite:
        redirect(URL('invite'))
    r.update_record(invitation_code=generate_invitation_code())
    redirect(URL('invite', vars=dict(reason="Your invitation code has been regenerated")))


@action('info')
@action.uses(auth, 'info.html')
def info():
    return dict()


@action('privacy')
@action.uses(auth, 'privacy.html')
def info():
    return dict()


@action('_ah/warmup')
def warmup():
    return "ok"


@action('/favicon.ico')
def favicon():
    return open('static/images/favicon.ico').read()


### API


@action('geolocation')
@action.uses(db, session, auth.user, url_signer.verify())
def geolocation():
    address = request.params.get('address')
    if address is None:
        return {}
    r = requests.get(GEOLOCATION_URL, params={
        "key": GEOLOCATION_KEY,
        "address": address})
    if r.status_code == 200:
        return r.json()
    else:
        raise HTTP(500)


@action('get_locations')
@action.uses(db, session, url_signer.verify())
def get_locations():
    loc_specified = False
    zipcode = request.params.get('zipcode')
    if zipcode is not None:
        # Tries via zipcode.
        r = db(db.zipcode.zipcode == zipcode).select().first()
        if r is not None:
            lat, lng = r.lat, r.lng
            loc_specified = True
    if not loc_specified:
        appengine_loc = request.get_header("X-Appengine-CityLatLong")
        if appengine_loc is not None:
            locs = appengine_loc.split(",")
            lat, lng = float(locs[0]), float(locs[1])
        else:
            return dict(
                locations=[],
                loc_specified=False,
            )
    # Gets many locations from center.
    locations = get_concentric_results(
        db, lat, lng, max_results=MAX_VIEW_RESULTS, enough_results=ENOUGH_RESULTS)
    return dict(
        locations=locations,
        loc_specified=loc_specified,
        fields=LOCATION_FIELDS,
    )


@action('edit_callback', method='GET')
@action.uses(db, session, url_signer.verify())
def edit_callback():
    lat_max = float(request.params.get('lat_max'))
    lat_min = float(request.params.get('lat_min'))
    lng_max = float(request.params.get('lng_max'))
    lng_min = float(request.params.get('lng_min'))
    live_results, maybe_incomplete = get_results_in_region(
        db, lat_max, lat_min, lng_max, lng_min, is_deleted=False,
        max_results=MAX_MAP_RESULTS)
    dead_results = []
    if request.params.get('include_deleted') == "true":
        dead_results, _ = get_results_in_region(
            db, lat_max, lat_min, lng_max, lng_min, is_deleted=False,
            max_results=MAX_MAP_RESULTS)
    # Remembers which results the user has requested.
    session['requested_ids'] = [x['id'] for x in live_results] + [x['id'] for x in dead_results]
    return dict(
        locations=live_results,
        deleted_locations=dead_results,
        maybe_incomplete=maybe_incomplete,
        fields=LOCATION_FIELDS,
    )


@action('edit_callback', method='POST')
@action.uses(db, session, auth.user, url_signer.verify())
def post_edit():
    """Stores an edit, returning the ID if any."""
    if request.json.get('is_vote'):
        # This is a vote.
        id = request.json.get('id')
        mz = request.json.get('mz')
        # As a safety measure, we only accept edits for results the user has obtained.
        if id in session.get('requested_ids', []):
            register_vote(id, max_zoom=mz)
        return "ok"
    loc = request.json.get('loc')
    id = loc.get('id')
    if loc is None:
        return "ok" # Silent discard.
    if id is not None and id not in session.get('requested_ids', []):
        return "ok" # Silent discard.
    if not loc.get('name'):
        # No empty names.
        return HTTP(500)
    d = {p: loc.get(p) for p in LOCATION_FIELDS}
    max_zoom = request.json.get('mz')
    edit_time = request.json.get('dt');
    # Sanitize.
    d['is_deleted'] = bool(d.get('is_deleted', False))
    new_id = perform_update(id, d, max_zoom=max_zoom, edit_time=edit_time)
    return dict(new_id=new_id)


def register_vote(id, max_zoom=None):
    """Registers a vote in favor of a location."""
    # Determines the location history id.
    loc_hist = db(db.location_history.location_id == id).select(orderby=~db.location_history.timestamp).first()
    if loc_hist is None:
        return
    u = get_user_email()
    db.vote.update_or_insert(
        ((db.vote.location_history_id == loc_hist.id) & (db.vote.author == u)),
        location_history_id=loc_hist.id,
        author=u,
        max_zoom=max_zoom,
    )


def perform_update(id, d, max_zoom=None, edit_time=None):
    """Performs the update corresponding to dictionary d, noting the
    outcome in the location history."""
    # Computes the square10.
    d['square10'] = latlng_to_square10(d.get('lat', 0), d.get('lng', 0))
    cleanup(d, ['id', 'author', 'date_created', 'date_updated'])
    if id is not None:
        # Update.
        db(db.location.id == id).update(**d)
        d['location_id'] = id
        new_id = None
    else:
        # Insert.
        new_id = db.location.insert(**d)
        d['location_id'] = new_id
    # Updates the history.
    db.location_history.insert(max_zoom=max_zoom, edit_time=edit_time, **d)
    return new_id


# @action('initdb')
# @action.uses(auth.user)
# def initdb():
#     cleardb()
#     for d in TEST_LOCATIONS:
#         perform_update(None, d)
#     return "ok"
#
# @action('cleardb')
# @action.uses(auth.user)
# def cleardb():
#     db(db.location).delete()
#     db(db.location_history).delete()
#     db(db.vote).delete()
#

# @action('storezips')
# @action.uses(db)
# def storezips():
#     # Reads zip code database.
#     import json
#     import os
#     APP_FOLDER = os.path.dirname(__file__)
#     ZIP_FILE = os.path.join(APP_FOLDER, "data", "zips.json")
#     with open(ZIP_FILE, "r") as f:
#         ZIPCODE_LOCATIONS = json.load(f)
#     for z, (lat, lng) in ZIPCODE_LOCATIONS.items():
#         db.zipcode.insert(zipcode=z, lat=lat, lng=lng)
#     return "ok"

@action('grantinitial')
@action.uses(db)
def grantinitial():
    r = db(db.userinfo.email == "luca.de.alfaro@gmail.com").select().first()
    if r is None:
        db.userinfo.insert(
            email="luca.de.alfaro@gmail.com",
            can_edit=True,
            can_invite=True,
            invited_by=None,
            invitation_code=generate_invitation_code(),
        )
        return "ok"
    return "exists"
