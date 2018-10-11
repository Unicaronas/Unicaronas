from project.tasks import send_webhook
from .serializers import WebhookSerializer


class BaseWebhook(object):
    """Base webhook class

    implements basic webhook actions
    """

    timeout = 5
    serializer_class = None

    def __init__(self, event, payload, recipients):
        assert isinstance(payload, dict)
        assert isinstance(recipients, list)
        assert isinstance(event, str)
        self._event = event
        self._payload = payload
        self._recipients = recipients
        self._data = None

    @property
    def event(self):
        return self._event

    @property
    def payload(self):
        """normalize"""
        return self._payload

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer_context(self):
        return {}

    def get_serializer(self, data, context={}):
        return self.get_serializer_class()(data=data, context=context)

    def get_data(self, *args, **kwargs):
        """Serialize event and payload"""
        if self._data is None:
            # build data from event and payload
            data = {
                'event': self.event,
                'payload': self.payload
            }
            context = self.get_serializer_context()
            serializer = self.get_serializer(data, context)
            serializer.is_valid()
            self._data = serializer.validated_data
        return self._data

    @property
    def recipients(self):
        """Clean recipients, removing invalid ones"""
        return self._recipients

    def send_one(self, recipient, data):
        """Send one webhook"""
        send_webhook.delay(recipient, data, self.timeout)

    def send(self):
        for recipient in self.recipients:
            self.send_one(recipient, self.get_data())


class BaseMultiplePayloadsWebhook(BaseWebhook):

    def __init__(self, event, payload, recipients):
        assert isinstance(payload, list)
        assert isinstance(recipients, list)
        assert isinstance(event, str)
        self._event = event
        self._payload = payload
        self._recipients = recipients
        self._data = None

    def get_data(self, *args, **kwargs):
        """Serialize event and payload"""
        # build data from event and payload
        data = []
        for payload in self.payload:
            temp = {
                'event': self.event,
                'payload': payload
            }
            context = self.get_serializer_context()
            serializer = self.get_serializer(temp, context)
            serializer.is_valid()
            data.append(serializer.validated_data)
        return data

    def send(self):
        for recipient, data in zip(self.recipients, self.get_data()):
            self.send_one(recipient, data)


class Webhook(BaseWebhook):
    serializer_class = WebhookSerializer


class MultiplePayloadsWebhook(BaseMultiplePayloadsWebhook):
    serializer_class = WebhookSerializer
