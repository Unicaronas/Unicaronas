from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core import validators
from oauth2_provider.settings import oauth2_settings
from project.utils import import_current_version_module
from alarms.tasks import dispatch_alarms
from .exceptions import PassengerBookedError, TripFullError, PassengerNotBookedError, UserNotDriverError, PassengerApprovedError, PassengerDeniedError, PassengerPendingError, NotEnoughSeatsError
from .utils import user_is_driver
from .tasks import publish_new_trip_on_fb
# Create your models here.


trips_webhooks = import_current_version_module('trips', 'webhooks')


class Trip(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        related_name='trips_offered',
        on_delete=models.SET_NULL,  # Null users are users that deleted their accounts
        null=True
    )
    origin = models.CharField(
        "Enderço de origem da carona",
        max_length=500
    )
    origin_point = models.PointField("Coordenadas de origem da carona")
    origin_address_components = JSONField(
        default=list,
        verbose_name='Componentes do endereço de origem',
        null=True
    )
    destination = models.CharField(
        "Enderço de destino da carona",
        max_length=500
    )
    destination_point = models.PointField("Coordenadas de destino da carona")
    destination_address_components = JSONField(
        default=list,
        verbose_name='Componentes do endereço de origem',
        null=True
    )
    price = models.PositiveSmallIntegerField("Preço da carona em reais")
    datetime = models.DateTimeField("Datetime de saída da carona")
    max_seats = models.PositiveSmallIntegerField(
        "Máximo número de assentos na carona",
        default=4,
        validators=[validators.MaxValueValidator(10)]
    )
    auto_approve = models.BooleanField(
        "Aprovação automática de passageiros",
        default=True
    )
    details = models.TextField(
        "Detalhes fornecidos pelo motorista", blank=True)
    application = models.ForeignKey(
        oauth2_settings.APPLICATION_MODEL,
        related_name='created_trips',
        on_delete=models.SET_NULL,
        null=True
    )

    def get_address_component(self, component, source, short=False):
        attr = 'short_name' if short else 'long_name'
        try:
            return next(filter(lambda comp: component in comp['types'], getattr(self, source))).get(attr)
        except StopIteration:
            return None

    def get_origin_adm_area_2(self, short=False):
        return self.get_address_component('administrative_area_level_2', 'origin_address_components', short)

    def get_origin_adm_area_1(self, short=False):
        return self.get_address_component('administrative_area_level_1', 'origin_address_components', short)

    def get_destination_adm_area_2(self, short=False):
        return self.get_address_component('administrative_area_level_2', 'destination_address_components', short)

    def get_destination_adm_area_1(self, short=False):
        return self.get_address_component('administrative_area_level_1', 'destination_address_components', short)

    def get_seats_left(self):
        """Quantos assentos restam na carona
        Apenas passageiros em espera e confirmados são considerados
        """
        seats_taken = self.passengers.exclude(
            status="denied"
        ).aggregate(seats_taken=Coalesce(Sum('seats'), 0))['seats_taken']
        return max(0, self.max_seats - seats_taken)

    @property
    def is_full(self):
        return self.get_seats_left() == 0

    def has_n_seats(self, seats):
        return self.get_seats_left() >= seats

    def check_is_passenger(self, user, raise_on_error=True):
        """Checks whether the user is a passenger. Raises error if not"""
        passenger = self.passengers.filter(user=user).first()
        if passenger is None and raise_on_error:
            raise PassengerNotBookedError("Passageiro não está nessa carona")
        return passenger

    def check_is_not_passenger(self, user, raise_on_error=True):
        """Checks whether the user is not a passenger. Raises error if is"""
        passenger = Passenger.objects.filter(user=user, trip=self).first()
        if passenger is not None and raise_on_error:
            raise PassengerBookedError("Usuário é passageiro nessa carona")
        return passenger

    def book_user(self, user, seats):
        """to-be Passenger books the trip"""
        if self.is_full:
            raise TripFullError("Carona cheia")
        if not self.has_n_seats(seats):
            raise NotEnoughSeatsError("Sem assentos suficientes")
        self.check_is_not_passenger(user)

        passenger = Passenger(
            user=user,
            trip=self,
            seats=seats
        )
        passenger.save()
        if self.auto_approve:
            passenger = self.approve_passenger(user)
            self.user.driver.notify_new_passenger(passenger)
            return
        trips_webhooks.PassengerPendingWebhook(passenger).send()
        self.user.driver.notify_new_passenger(passenger)

    def approve_passenger(self, user):
        """
        Driver approves the passenger (or is automatically approved)
        Also allows driver to approve denied passengers
        """
        passenger = self.check_is_passenger(user)
        passenger.approve()
        return passenger

    def deny_passenger(self, user):
        """
        Driver decides to deny a pending passenger
        """
        passenger = self.check_is_passenger(user)
        passenger.deny()

    def forfeit_passenger(self, user):
        """
        Driver decides to deny a passanger after accepting them
        """
        passenger = self.check_is_passenger(user)
        passenger.forfeit()

    def passenger_give_up(self, user):
        """Passenger decides to leave the trip"""
        passenger = self.check_is_passenger(user)
        if passenger.status == 'denied':
            raise PassengerDeniedError('Passageiro está negado')
        self.user.driver.notify_passenger_give_up(passenger)
        passenger.give_up()

    def delete_trip(self):
        for passenger in self.passengers.exclude(status='denied'):
            passenger.trip_deleted()
        self.delete()

    @classmethod
    def create_trip(cls, user, **kwargs):
        """Creates a trip, checking if the user is a driver"""
        if not user_is_driver(user):
            raise UserNotDriverError(user.get_full_name() + ' não é motorista')
        trip = cls.objects.create(user=user, **kwargs)

        # Dispatch alarms announcing the new trip to users
        dispatch_alarms.delay(trip.id)
        # Publish on Facebook if enabled
        publish_new_trip_on_fb.delay(trip.id)
        return trip

    def __str__(self):
        return f"Carona de {self.user}, em {self.datetime}"


STATUS_CHOICES = (
    ('approved', 'approved'),
    ('pending', 'pending'),
    ('denied', 'denied')
)


class Passenger(models.Model):
    user = models.ForeignKey(
        User,
        related_name='trips_taken',
        on_delete=models.SET_NULL,  # Null users are users that deleted their accounts
        null=True
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='passengers'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    book_time = models.DateTimeField(
        "Hora que o passageiro fez a reserva",
        auto_now_add=True
    )
    seats = models.PositiveSmallIntegerField(
        "Número de assentos reservados",
        default=1
    )

    def approve(self):
        if self.status == 'approved':
            raise PassengerApprovedError('Passageiro já aprovado')
        self.status = 'approved'
        self.save()
        trips_webhooks.PassengerApprovedWebhook(self).send()

    def deny(self):
        if self.status == 'denied':
            raise PassengerDeniedError('Passageiro já negado')
        elif self.status == 'approved':
            raise PassengerApprovedError('Passageiro já aprovado')
        self.status = 'denied'
        self.save()
        trips_webhooks.PassengerDeniedWebhook(self).send()
        # if the trip was full and now it is not, send alarms
        if self.trip.get_seats_left() == 1:
            dispatch_alarms.delay(self.trip.id)

    def forfeit(self):
        if self.status == 'denied':
            raise PassengerDeniedError('Passageiro já negado')
        elif self.status == 'pending':
            raise PassengerPendingError('Passageiro ainda pendente')
        self.status = 'denied'
        self.save()
        trips_webhooks.PassengerForfeitWebhook(self).send()
        # if the trip was full and now it is not, send alarms
        if self.trip.get_seats_left() == 1:
            dispatch_alarms.delay(self.trip.id)

    def trip_deleted(self):
        trips_webhooks.TripDeletedWebhook(self).send()

    def give_up(self):
        # if the trip was full and now it is not, send alarms
        if self.trip.is_full:
            dispatch_alarms.delay(self.trip.id)
        self.delete()

    def __str__(self):
        return f"Passageiro {self.user} na {self.trip}"
