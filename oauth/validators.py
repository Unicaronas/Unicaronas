import re
from oauth2_provider.validators import WildcardSet, URIValidator


class URISchemeWildcardSet(WildcardSet):
    """
    A set that always returns True on `in` if
    the comparing item is a valid scheme
    """

    def __contains__(self, item):
        if not isinstance(item, str):
            return False
        scheme_re = URIValidator.scheme_re
        item = item + '://' if not item.endswith('://') else item
        return re.match(scheme_re, item, re.I)
