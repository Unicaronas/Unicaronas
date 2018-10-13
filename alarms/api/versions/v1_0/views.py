from django.utils import timezone
from rest_framework import viewsets
from project.mixins import PrefetchQuerysetModelMixin
from oauth2_provider.contrib.rest_framework.permissions import TokenMatchesOASRequirements
from .serializers import AlarmCreateSerializer, AlarmListRetrieveSerializer
from ....models import Alarm


class AlarmViewset(
        PrefetchQuerysetModelMixin,
        viewsets.ModelViewSet):

    lookup_field = 'id'
    serializer_class = AlarmCreateSerializer
    queryset = Alarm.objects.all()
    max_limit = 50
    limit = 10
    swagger_tags = ['Alarmes']
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["alarms:read"]],
        "POST": [["alarms:write"]],
        "PUT": [["alarms:write"]],
        "PATCH": [["alarms:write"]],
        "DELETE": [["alarms:write"]]
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Only allow editing and viewing the user's alarms
        qs = qs.filter(user=self.request.user)
        # If the alarm already happened, only allow GET
        if self.request.method != 'GET':
            qs = qs.filter(datetime_lte__gte=timezone.now())
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AlarmListRetrieveSerializer
        return AlarmCreateSerializer
