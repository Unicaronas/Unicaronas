from django.shortcuts import reverse
from django.conf import settings
from oauth2_provider.models import get_access_token_model, get_application_model
from project.utils import local_versioned_url_name
from project.webhooks import MultiplePayloadsWebhook


class BaseDriverWebhook(MultiplePayloadsWebhook):
    event = None
    permissions = None
    passenger_allows_field = None

    def __init__(self, passenger):
        trip = passenger.trip
        if self.driver_allows(trip.user):
            payload, recipients = self.get_payload_recipients(passenger)
        else:
            payload, recipients = ([], [])
        super().__init__(self.event, payload, recipients)

    def get_valid_apps(self, user):
        access_tokens = get_access_token_model().objects.filter(
            user=user
        )
        valid_access_tokens = [token for token in access_tokens if token.allow_scopes(self.permissions)]

        return get_application_model().objects.exclude(
            webhook_url__isnull=True
        ).exclude(
            webhook_url__exact=''
        ).filter(
            accesstoken__in=valid_access_tokens
        ).distinct()

    def get_payload_recipients(self, passenger):
        trip = passenger.trip
        user = trip.user
        recipients = []
        payload = []
        for app in self.get_valid_apps(user):
            recipients.append(app.webhook_url)
            user_id = app.get_scoped_user_id(app, user)
            trip_id = trip.id
            payload.append(
                {
                    'user_id': user_id,
                    'trip_id': trip_id,
                    'resource_url': settings.ROOT_URL + reverse(local_versioned_url_name('api:driver-trips-passengers-detail', __file__, 2), kwargs={
                        'trip_id': trip.id,
                        'passenger_user_id': app.get_scoped_user_id(app, passenger.user)
                    })
                }
            )
        return payload, recipients

    def driver_allows(self, user):
        if self.passenger_allows_field is None:
            return True
        return getattr(user.preferences, self.passenger_allows_field, False)


class DriverNewPassengerPendingWebhook(BaseDriverWebhook):
    """New Pending Passenger Webhook

    Webhook that sends notifications that
    a new passenger is pending on a trip owned by the user
    """

    permissions = ['trips:driver:read']
    event = 'driver_passenger_pending'
    passenger_allows_field = 'updates_notifications'


class DriverNewPassengerApprovedWebhook(BaseDriverWebhook):
    """New Passenger Approved Webhook

    Webhook that sends notifications that
    a new passenger is approved on a trip owned by the user
    """

    permissions = ['trips:driver:read']
    event = 'driver_passenger_approved'
    passenger_allows_field = 'updates_notifications'


class DriverPassengerGiveUpWebhook(BaseDriverWebhook):
    """Passenger gave up on trip

    Webhook that sends notifications that
    a passenger has given up on a trip owned by the user
    """

    permissions = ['trips:driver:read']
    event = 'driver_passenger_give_up'
    passenger_allows_field = 'updates_notifications'

    def get_payload_recipients(self, passenger):
        recipients = []
        payload = []
        trip = passenger.trip
        user = trip.user
        for app in self.get_valid_apps(user):
            recipients.append(app.webhook_url)
            user_id = app.get_scoped_user_id(app, user)
            payload.append(
                {
                    'user_id': user_id,
                    'trip_id': trip.id,
                    'passenger': {
                        'first_name': passenger.user.first_name,
                        'last_name': passenger.user.last_name
                    },
                    'resource_url': settings.ROOT_URL + reverse(local_versioned_url_name('api:driver-trips-detail', __file__, 2), kwargs={'id': trip.id})
                }
            )
        return payload, recipients
