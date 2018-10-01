def get_search_keys():
    return ['facebook', 'blablacar']


def get_search_values():
    from .search import FacebookSearch, BlaBlaCarSearch
    return [FacebookSearch(), BlaBlaCarSearch()]


def get_search_map():
    keys = get_search_keys()
    values = get_search_values()
    return {keys[i]: values[i] for i in range(len(keys))}
