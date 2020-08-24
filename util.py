
def cleanup(d, el_list):
    """Remove list of elements from a dictionary."""
    for el in el_list:
        if el in d:
            del d[el]
