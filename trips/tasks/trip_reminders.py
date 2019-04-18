from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from project.celery import app as celery_app
from project.utils import import_current_version_module
from .util import encode_task_uuid


trips_webhooks = import_current_version_module('trips', 'webhooks')


@shared_task
def send_driver_reminder(trip_id):
    from ..models import Trip
    trip = Trip.objects.filter(pk=trip_id).first()
    if trip:
        trips_webhooks.DriverReminderWebhook(trip).send()


@shared_task
def send_passenger_reminder(passenger_id):
    from ..models import Passenger
    passenger = Passenger.objects.filter(pk=passenger_id).first()
    if passenger:
        trips_webhooks.PassengerReminderWebhook(passenger).send()


class TripReminder(object):
    """Trip Reminder
    Schedules and Unschedules the execution of
    trip reminders for both passengers and drivers
    """

    # Tuple of hours before trip and execution ttl
    reminder_hour_timeouts = (
        (72, 48),   # if 3 days before trip, schedule a reminder 2 days before
        (24, 12),   # If 24 hours before trip, schedule a reminder 12 hours before
        (3, 1)  # If 3 hours before trip, schedule reminder 1 hour before
    )

    reminder_types = (
        'passenger_reminder',
        'driver_reminder'
    )

    def __init__(self, reminder_type, obj):
        assert reminder_type in self.reminder_types
        self.reminder_type = reminder_type
        self.object = obj

    @property
    def task(self):
        tasks = {
            'passenger_reminder': send_passenger_reminder,
            'driver_reminder': send_driver_reminder
        }
        return tasks[self.reminder_type]

    @property
    def trip(self):
        obj = self.object
        if self.reminder_type == 'passenger_reminder':
            return obj.trip
        elif self.reminder_type == 'driver_reminder':
            return obj

    def get_task_id(self, time):
        return encode_task_uuid(self.reminder_type, str(self.object.id), str(time))

    def schedule_execution(self, time):
        encoded_id = self.get_task_id(time)
        eta = self.trip.datetime - timedelta(hours=time)
        self.task.apply_async(args=[self.object.id], task_id=encoded_id, eta=eta)

    def schedule(self):
        now = timezone.now()
        hours_to_trip = (self.trip.datetime - now).total_seconds() / 3600

        for _, timeout in filter(lambda x: x[0] < hours_to_trip, self.reminder_hour_timeouts):
            self.schedule_execution(timeout)

    def unschedule(self):
        for _, timeout in self.reminder_hour_timeouts:
            task_id = self.get_task_id(timeout)
            celery_app.control.revoke(task_id, terminate=True)
