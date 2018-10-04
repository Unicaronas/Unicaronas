from .cache import RedisCache
from .date_time import find_datetime
from .price import find_price
from .is_valid import is_valid
from .origin_destination import find_origin_destination

from ..result import ResultItem


def unique_id(item):
    return item['id']


def process_item(item, source=None):
    if not is_valid(item):
        return None
    # Cache items for 1 day
    cache = RedisCache(timeout=86400)

    uid = unique_id(item)

    # Try to find uid in cache
    result = cache.get_key(uid)
    if result is not None:
        # Return it if found
        return result

    # If not found, calculate all attributes
    price = find_price(item)
    if price is None:
        # TODO: Save failure to database
        return None

    date_time = find_datetime(item)
    if date_time is None:
        # TODO: Save failure to database
        return None

    origin_destination = find_origin_destination(item)
    if origin_destination is None:
        # TODO: Save failure to database
        return None

    url = f"https://facebook.com/{item['id']}"

    # Generate result item
    result = ResultItem(
        origin=origin_destination[0],
        destination=origin_destination[1],
        price=price,
        date_time=date_time,
        url=url,
        source=source
    )
    # Cache it
    cache.set_key(uid, result)
    return result
