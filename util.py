import numpy as np
import hashlib, uuid

from .constants import *

def cleanup(d, el_list):
    """Remove list of elements from a dictionary."""
    for el in el_list:
        if el in d:
            del d[el]
    return d

def latlngidx_to_square10(lat_idx, lng_idx):
    return "%d;%d" % (lat_idx, lng_idx)

def latlng_to_square10(lat, lng):
    lat_idx = int(lat / SQSIZE)
    lng_idx = int(lng / SQSIZE)
    return latlngidx_to_square10(lat_idx, lng_idx)

def query_square(db, sq, is_deleted=False):
    """Returns the results for a given square."""
    return db((db.location.square10 == sq) &
              (db.location.is_deleted == is_deleted)).select().as_list()


def get_results_in_region(db, lat_max, lat_min, lng_max, lng_min,
                          is_deleted=False, max_results=25, max_radius=DMAX):
    """Returns the list of results in a given rectangle, for either
    normal locations (is_deleted=False) or deleted locations (is_delete=True).
    Tries to minimize queries not to get more than max_results.
    Returns a list of results, and a flag indicating that the results may be incomplete.
    """
    results = {}
    maybe_incomplete = False
    # Computes how many squares are needed.
    lat_min_idx = int(lat_min / SQSIZE)
    lat_max_idx = int(lat_max / SQSIZE)
    lat_c_idx = int((lat_max - lat_min) / (2 * SQSIZE))
    lng_min_idx = int(lng_min / SQSIZE)
    lng_max_idx = int(lng_max / SQSIZE)
    lng_c_idx = int((lng_max - lng_min) / (2 * SQSIZE))
    lat_n = lat_max_idx - lat_min_idx + 1
    lng_n = lng_max_idx - lng_min_idx + 1
    # If there are too many, just takes the center 3x3.
    if lat_n > 3:
        maybe_incomplete = True
        lat_idxs = list(range(lat_c_idx - 1, lat_c_idx + 2))
    else:
        lat_idxs = list(range(lat_min_idx, lat_max_idx + 1))
    if lng_n > 3:
        maybe_incomplete = True
        lng_idxs = list(range(lng_c_idx - 1, lng_c_idx + 2))
    else:
        lng_idxs = list(range(lng_min_idx, lng_max_idx + 1))
    num_squares = len(lat_idxs) * len(lng_idxs)
    # Queries the squares.
    for lat_idx in lat_idxs:
        for lng_idx in lng_idxs:
            sq = latlngidx_to_square10(lat_idx, lng_idx)
            resl = query_square(db, sq, is_deleted=is_deleted)
            results.update({r['id']: r for r in resl})
            if len(results) > max_results and num_squares > 1:
                maybe_incomplete = True
                break
        if len(results) > max_results and num_squares > 1:
            maybe_incomplete = True
            break
    # Filters results only in original view.
    clean_results = []
    for loc in results.values():
        if lat_min <= loc['lat'] <= lat_max and lng_min <= loc['lng'] <= lng_max:
            clean_results.append(loc)
    return clean_results, maybe_incomplete


def get_concentric_results(db, lat_c, lng_c, max_radius=DMAX,
                           good_radius=DGOOD, max_results=25, enough_results=1):
    """Returns the list of results around a given point, until either
    max_radius is reached, or until the max number of results is
    accummulated.  Returns the list of results.
    """
    squares = set()
    results = {}
    # Progressively enlarges.
    n = 0
    while True:
        num_points = 2 * n + 1
        lats = np.linspace(lat_c - n * SQSIZE, lat_c + n * SQSIZE, num_points)
        lngs = np.linspace(lng_c - n * SQSIZE, lng_c + n * SQSIZE, num_points)
        for lat in lats:
            for lng in lngs:
                sq = latlng_to_square10(lat, lng)
                if sq not in squares:
                    # The square is new.
                    resl = query_square(db, sq, is_deleted=False)
                    results.update({r['id']: r for r in resl})
                    if len(results) >= max_results:
                        break
                squares.add(sq)
            if len(results) >= max_results:
                break
        # We got enough results.
        if len(results) >= max_results:
            break
        # We got some results.
        if len(results) >= enough_results and n > good_radius / SQSIZE:
            break
        # We looked at all squares.
        if n > max_radius / SQSIZE:
            break
        n += 1
    return list(results.values())


def generate_invitation_code():
    s = str(uuid.uuid1())
    h = hashlib.sha1(s.encode('utf8'))
    t = h.hexdigest()
    n = len(t)
    p = [t[4 * i : 4 * (i + 1)] for i in range((n + 1) // 4)]
    return "-".join(p)