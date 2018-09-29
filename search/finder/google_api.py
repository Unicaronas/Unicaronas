from ..result import Result
from .base import BaseFinder
from ..geocoding import geocode_address


class GoogleAPIFinder(BaseFinder):
    """Google API Finder
    Uses google's api to fetch the data
    Only to be used as a last resort
    """

    def _search(self, term):
        try:
            addr, point = geocode_address(term.query)
        except ValueError:
            # Google API error or no results
            return None
        return Result(term.query, addr, point)
