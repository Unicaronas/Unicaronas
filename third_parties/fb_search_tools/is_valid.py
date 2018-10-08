import re


def is_valid(item):
    """Is Valid
    True if is a offering and not full. False otherwise
    """
    message = item['message']
    return re.search('oferec', message) and not (
        re.search('lotad', message) or
        re.search('loto', message)
    )
