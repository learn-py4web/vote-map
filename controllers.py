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
    lat_max = request.params.get('lat_max')
    lat_min = request.params.get('lat_min')
    lng_max = request.params.get('lng_max')
    lng_min = request.params.get('lng_min')
    return dict(
        locations=TEST_LOCATIONS
    )



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

