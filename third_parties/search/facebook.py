from .base import BaseThirdPartySearch
from ..connection import FacebookConnection


class FacebookSearch(BaseThirdPartySearch):

    def __init__(self, fb_group_id):
        conn = FacebookConnection(fb_group_id)
        super().__init__(conn)
