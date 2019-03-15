from celery import shared_task
from ..models import Alarm


@shared_task
def dispatch_alarms(trip_id):
    """Dispatch alarms
    Given a newly created trip,
    dispatch all related alarms
    """
    from trips.models import Trip
    trip = Trip.objects.filter(id=trip_id).first()
    if trip is not None:
        Alarm.find_and_send(trip)
