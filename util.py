
def cleanup(d, el_list):
    """Remove list of elements from a dictionary."""
    for el in el_list:
        if el in d:
            del d[el]
    return d

def lat_long_to_square10(lat, lng):
    return "%.0f;%.0f" % (lat * 10, lng * 10)

