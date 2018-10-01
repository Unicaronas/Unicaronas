from .base import BaseThirdPartySearch
from ..connection import BlaBlaCarConnection


class BlaBlaCarSearch(BaseThirdPartySearch):

    def __init__(self):
        conn = BlaBlaCarConnection()
        super().__init__(conn)
