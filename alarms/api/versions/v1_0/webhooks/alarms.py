from django.utils import timezone
from django.shortcuts import reverse
from django.conf import settings
from oauth2_provider.models import get_access_token_model, get_application_model
from project.webhooks import MultiplePayloadsWebhook
from project.utils import local_versioned_url_name


class BaseAlarmWebhook(MultiplePayloadsWebhook):
    event = None
    permissions = None

    def __init__(self, alarm, trip):
        payload, recipients = self.get_payload_recipients(alarm, trip)
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

    def get_payload_recipients(self, alarm, trip):
        user = alarm.user
        trip_url = settings.ROOT_URL + reverse(local_versioned_url_name('api:search-trips-detail', __file__, 2), kwargs={'pk': trip.id})
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


class BaseMultipleAlarmsWebhook(BaseAlarmWebhook):
    def __init__(self, alarms, trip):
        payload = []
        recipients = []
        for alarm in alarms:
            p, r = self.get_payload_recipients(alarm, trip)
            payload.extend(p)
            recipients.extend(r)
        super().__init__(self.event, payload, recipients)


class AlarmWebhook(BaseAlarmWebhook):
    """Alarm Webhook

    Webhook that sends notifications that
    a user is now pending on a trip
    """

    permissions = ['trips:passenger:read']
    event = 'passenger_alarm'


class MultipleAlarmsWebhook(BaseMultipleAlarmsWebhook):
    """Multiple Alarms Webhook

    Webhook that sends notifications that
    a user is now pending on a trip
    """

    permissions = ['trips:passenger:read']
    event = 'passenger_alarm'
