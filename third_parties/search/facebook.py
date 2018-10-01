from .base import BaseThirdPartySearch
from ..connection import FacebookConnection


class FacebookSearch(BaseThirdPartySearch):

    def __init__(self):
        conn = FacebookConnection()
        super().__init__(conn)
