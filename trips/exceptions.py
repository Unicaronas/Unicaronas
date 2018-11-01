class BasePassengerException(Exception):
    """Base passenger exception"""


class BaseTripException(Exception):
    """Base trip exception"""


class BaseDriverException(Exception):
    """Base trip exception"""


class TripFullError(BaseTripException):
    """The trip is already full"""


class NotEnoughSeatsError(BaseTripException):
    """Not enough seats on a trip"""


class PassengerBookedError(BasePassengerException):
    """The passeger has alrady booked for this specific trip
    includes approved, denied and forfeit passengers
    """


class PassengerNotBookedError(BasePassengerException):
    """The passeger is not booked for this specific trip"""


class UserNotDriverError(BaseDriverException):
    """The user is not a driver"""


class PassengerApprovedError(BasePassengerException):
    """This passenger is already approved"""


class PassengerDeniedError(BasePassengerException):
    """This passenger is already denied/forfeit"""


class PassengerPendingError(BasePassengerException):
    """This passenger is still pending"""
