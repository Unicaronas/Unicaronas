from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.core import validators
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.utils import timezone
from project.utils import import_current_version_module
# Create your models here.


alarm_webhooks = import_current_version_module('alarms', 'webhooks')


class Alarm(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        related_name='alarms',
        on_delete=models.CASCADE
    )
    origin = models.CharField(
        "Enderço de origem da carona",
        max_length=500
    )
    origin_point = models.PointField("Coordenadas de origem da carona")
    origin_radius = models.FloatField(
        "Raio de pesquisa da origem em km",
        default=5,
        validators=[validators.MaxValueValidator(10), validators.MinValueValidator(0.05)],
    )
    destination = models.CharField(
        "Enderço de destino da carona",
        max_length=500
    )
    destination_point = models.PointField("Coordenadas de destino da carona")
    destination_radius = models.FloatField(
        "Raio de pesquisa do destino em km",
        default=5,
        validators=[validators.MaxValueValidator(20), validators.MinValueValidator(0.05)],
    )
    price = models.PositiveSmallIntegerField("Preço máximo da carona em reais", null=True)
    auto_approve = models.NullBooleanField("Aprovação automática de passageiros", null=True)
    datetime_lte = models.DateTimeField("Datetime máxima de saída da carona", null=True)
    datetime_gte = models.DateTimeField("Datetime mínima de saída da carona", null=True)
    min_seats = models.PositiveSmallIntegerField(
        "Mínimo número de assentos na carona",
        validators=[validators.MaxValueValidator(10)],
        null=True
    )

    @classmethod
    def find_and_send(cls, trip):
        """Find and send alarms
        Takes a newly created trip and searches
        through all alarms to find matches.
        If any are found, send them.
        """

        # Start by filtering the easy ones
        # and then filter using expensive fields
        alarms = cls.objects.exclude(
            # Alarms that already ended should not be queried
            Q(datetime_lte__isnull=False) & Q(datetime_lte__lte=timezone.now())
        ).filter(
            # If the alarm defined auto_approve, filter it
            Q(auto_approve__isnull=True) | Q(auto_approve=trip.auto_approve)
        ).filter(
            # If the alarm defined price, filter it
            Q(price__isnull=True) | Q(price__gte=trip.price)
        ).filter(
            # If the alarm defined min_seats, filter it
            Q(min_seats__isnull=True) | Q(min_seats__lte=trip.max_seats)
        ).filter(
            # If the alarm defined datetime_gte, filter it
            Q(datetime_gte__isnull=True) | Q(datetime_gte__lte=trip.datetime)
        ).filter(
            # If the alarm defined datetime_lte, filter it
            Q(datetime_lte__isnull=True) | Q(datetime_lte__gte=trip.datetime)
        ).annotate(
            # First annotate the distances, since django can't compute
            # F expressions inside D functions, per
            # https://gis.stackexchange.com/questions/176735/geodjango-distance-filter-based-on-database-column
            origin_distance=Distance('origin_point', trip.origin_point),
            destination_distance=Distance('destination_point', trip.destination_point)
        ).filter(
            # Filter origin
            origin_distance__lte=F('origin_radius') * 1000
        ).filter(
            # Filter destination
            destination_distance__lte=F('destination_radius') * 1000
        )
        alarm_webhooks.MultipleAlarmsWebhook(alarms, trip).send()
        # Clear selected alarms
        alarms.delete()
