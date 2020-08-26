import numpy as np
from .constants import *

def cleanup(d, el_list):
    """Remove list of elements from a dictionary."""
    for el in el_list:
        if el in d:
            del d[el]
    return d

def latlng_to_square10(lat, lng):
    return "%.0f;%.0f" % (lat / SQSIZE, lng / SQSIZE)


def query_square(db, sq, is_deleted=False):
    """Returns the results for a given square."""
    return db((db.location.square10 == sq) &
              (db.location.is_deleted == is_deleted)).select().as_list()


def get_results_in_region(db, lat_max, lat_min, lng_max, lng_min,
                          is_deleted=False, max_results=25):
    """Returns the list of results in a given rectangle, for either
    normal locations (is_deleted=False) or deleted locations (is_delete=True).
    Tries to minimize queries not to get more than max_results.
    Returns a list of results, and a flag indicating that the results may be incomplete.
    """
    results = {}
    # Determines the squares of the corner points.
    squares = {latlng_to_square10(x, y) for (x, y) in
               [(lat_max, lng_max), (lat_max, lng_min),
                (lat_min, lng_max), (lat_min, lng_min)]}
    maybe_incomplete = False
    if len(squares) == 1:
        sq = squares.pop()
        print("Searching for single square:", sq)
        # Looking at a single square is enough.
        resl = query_square(db, sq, is_deleted=is_deleted)
        results.update({r['id']: r for r in resl})
    else:
        # More than one square.  Goes from the center out.
        squares = set()
        lat_c = (lat_max + lat_min) / 2.
        lng_c = (lng_max + lng_min) / 2.
        # Progressively enlarges.
        n = 0
        while True:
            num_points = 2 * n + 1
            lats = np.linspace(lat_c - n * SQSIZE, lat_c + n * SQSIZE, num_points)
            lngs = np.linspace(lat_c - n * SQSIZE, lat_c + n * SQSIZE, num_points)
            for lat in lats:
                for lng in lngs:
                    sq = latlng_to_square10(lat, lng)
                    if sq not in squares:
                        # The square is new.
                        resl = query_square(db, sq, is_deleted=is_deleted)
                        results.update({r['id']: r for r in resl})
                        if len(results) > max_results:
                            break
                    squares.add(sq)
                if len(results) > max_results:
                    maybe_incomplete = True
                    break
            # We got enough results.
            if len(results) > max_results:
                maybe_incomplete = True
                break
            # We looked at all squares.
            if lats[0] < lat_min and lats[-1] > lat_max and lngs[0] < lng_min and lngs[-1] > lng_max:
                break
            n += 1
    # Filters results only in original view.
    clean_results = []
    for loc in results.values():
        if lat_min <= loc['lat'] <= lat_max and lng_min <= loc['lng'] <= lng_max:
            clean_results.append(loc)
    return clean_results, maybe_incomplete


def get_concentric_results(db, lat_c, lng_c, max_radius=1.,
                           max_results=25):
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
        lngs = np.linspace(lat_c - n * SQSIZE, lat_c + n * SQSIZE, num_points)
        for lat in lats:
            for lng in lngs:
                sq = latlng_to_square10(lat, lng)
                if sq not in squares:
                    # The square is new.
                    resl = query_square(db, sq, is_deleted=False)
                    results.update({r['id']: r for r in resl})
                    if len(results) > max_results:
                        break
                squares.add(sq)
            if len(results) > max_results:
                break
        # We got enough results.
        if len(results) > max_results:
            break
        # We looked at all squares.
        if n > max_radius / SQSIZE:
            break
        n += 1
    return list(results.values())