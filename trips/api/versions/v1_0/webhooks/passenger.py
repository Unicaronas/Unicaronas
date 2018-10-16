from django.utils import timezone
from django.shortcuts import reverse
from django.conf import settings
from oauth2_provider.models import get_access_token_model, get_application_model
from project.utils import local_versioned_url_name
from project.webhooks import MultiplePayloadsWebhook


class BasePassengerWebhook(MultiplePayloadsWebhook):
    event = None
    permissions = None
    passenger_allows_field = None

    def __init__(self, passenger):
        if self.passenger_allows(passenger.user):
            payload, recipients = self.get_payload_recipients(passenger)
        else:
            payload, recipients = ([], [])
        super().__init__(self.event, payload, recipients)

    def get_valid_apps(self, user):
        access_tokens = get_access_token_model().objects.filter(
            user=user,
            expires__gt=timezone.now()
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
        user = passenger.user
        trip = passenger.trip
        trip_url = settings.ROOT_URL + reverse(local_versioned_url_name('api:passenger-trips-detail', __file__, 2), kwargs={'pk': trip.id})
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
                    'resource_url': trip_url
                }
            )
        return payload, recipients

    def passenger_allows(self, user):
        if self.passenger_allows_field is None:
            return True
        return getattr(user.preferences, self.passenger_allows_field, False)


class PassengerPendingWebhook(BasePassengerWebhook):
    """Passenger Pending Webhook

    Webhook that sends notifications that
    a user is now pending on a trip
    """

    permissions = ['trips:passenger:read']
    event = 'passenger_pending'
    passenger_allows_field = 'updates_notifications'


class PassengerApprovedWebhook(BasePassengerWebhook):
    """Passenger Approved Webhook

    Webhook that sends notifications that
    a user is now approved on a trip
    """

    permissions = ['trips:passenger:read']
    event = 'passenger_approved'
    passenger_allows_field = 'updates_notifications'


class PassengerDeniedWebhook(BasePassengerWebhook):
    """Passenger Denied Webhook

    Webhook that sends notifications that
    a user is now denied on a trip
    """

    permissions = ['trips:passenger:read']
    event = 'passenger_denied'
    passenger_allows_field = 'updates_notifications'


class PassengerForfeitWebhook(BasePassengerWebhook):
    """Passenger Forfeit Webhook

    Webhook that sends notifications that
    a user is now forfeit on a trip
    """

    permissions = ['trips:passenger:read']
    event = 'passenger_forfeit'
    passenger_allows_field = 'updates_notifications'


class TripDeletedWebhook(BasePassengerWebhook):
    """Trip Deleted Webhook

    Webhook that sends notifications that
    a trip was deleted
    """

    permissions = ['trips:passenger:read']
    event = 'trip_deleted'
    passenger_allows_field = 'updates_notifications'

    def get_payload_recipients(self, passenger):
        recipients = []
        payload = []
        trip = passenger.trip
        user = passenger.user
        for app in self.get_valid_apps(user):
            recipients.append(app.webhook_url)
            user_id = app.get_scoped_user_id(app, user)
            payload.append(
                {
                    'user_id': user_id,
                    'origin': trip.origin,
                    'destination': trip.destination,
                    'datetime': trip.datetime
                }
            )
        return payload, recipients
