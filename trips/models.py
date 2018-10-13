from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core import validators
from oauth2_provider.settings import oauth2_settings
from project.utils import import_current_version_module
from .exceptions import PassengerBookedError, TripFullError, PassengerNotBookedError, UserNotDriverError, PassengerApprovedError, PassengerDeniedError, PassengerPendingError
from .utils import user_is_driver
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
    destination = models.CharField(
        "Enderço de destino da carona",
        max_length=500
    )
    destination_point = models.PointField("Coordenadas de destino da carona")
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

    def get_seats_left(self):
        """Quantos assentos restam na carona
        Apenas passageiros em espera e confirmados são considerados
        """
        return max(0, self.max_seats - self.passengers.exclude(status="denied").count())

    @property
    def is_full(self):
        return self.get_seats_left() == 0

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

    def book_user(self, user):
        """to-be Passenger books the trip"""
        if self.is_full:
            raise TripFullError("Carona cheia")
        self.check_is_not_passenger(user)

        passenger = Passenger(
            user=user,
            trip=self
        )
        passenger.save()
        if self.auto_approve:
            self.approve_passenger(user)
            self.user.driver.notify_new_passenger(user)
            return
        trips_webhooks.PassengerPendingWebhook(passenger).send()

    def approve_passenger(self, user):
        """
        Driver approves the passenger (or is automatically approved)
        Also allows driver to approve denied passengers
        """
        if self.is_full:
            raise TripFullError('Carona cheia')
        passenger = self.check_is_passenger(user)
        passenger.approve()

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
        passenger.give_up()
        self.user.driver.notify_passenger_give_up(user)

    def delete_trip(self):
        for passenger in self.passengers.all():
            passenger.trip_deleted()
        self.delete()

    @classmethod
    def create_trip(cls, user, **kwargs):
        """Creates a trip, checking if the user is a driver"""
        if not user_is_driver(user):
            raise UserNotDriverError(user.get_full_name() + ' não é motorista')
        trip = cls(user=user, **kwargs)
        trip.save()
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

    def forfeit(self):
        if self.status == 'denied':
            raise PassengerDeniedError('Passageiro já negado')
        elif self.status == 'pending':
            raise PassengerPendingError('Passageiro ainda pendente')
        self.status = 'denied'
        self.save()
        trips_webhooks.PassengerForfeitWebhook(self).send()

    def trip_deleted(self):
        trip = self.trip
        trips_webhooks.TripDeletedWebhook(
            self.user,
            trip.origin,
            trip.destination,
            trip.datetime,
            trip.user
        ).send()

    def give_up(self):
        self.delete()

    def __str__(self):
        return f"Passageiro {self.user} na {self.trip}"
