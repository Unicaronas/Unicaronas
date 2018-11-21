from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from project.utils import import_current_version_module
from .validators import UniRegexValidator
# Create your models here.


trips_webhooks = import_current_version_module('trips', 'webhooks')


GENDER_CHOICES = (
    ('male', 'Masculino'),
    ('female', 'Feminino'),
    ('other', 'Outro'),
    ('na', 'Prefiro não dizer')
)

TALKING_CHOICES = (
    ('Gosto de paisagens', 'Gosto de paisagens'),
    ('Às vezes curto conversar', 'Às vezes curto conversar'),
    ('Adoro conversar!', 'Adoro conversar!')
)

SMOKING_CHOICES = (
    ('Cigarro não, por favor', 'Cigarro não, por favor'),
    ('Às vezes permito fumar', 'Às vezes permito fumar'),
    ('Cigarro não me incomoda', 'Cigarro não me incomoda')
)

PET_CHOICES = (
    ('Animais não, por favor', 'Animais não, por favor'),
    ('Depende do animal', 'Depende do animal'),
    ('Adoro animais!', 'Adoro animais!')
)

MUSIC_CHOICES = (
    ('Curto silêncio', 'Curto silêncio'),
    ('Depende da música', 'Depende da música'),
    ('Adoro música!', 'Adoro música!')
)

UNIVERSITY_CHOICES = (
    ('unicamp', 'Unicamp'),
    ('pucc', 'PUC-Campinas'),
    ('usp', 'USP'),
    ('ifsp', 'IFSP')
)

UNIVERSITY_EMAIL_VALIDATORS = {
    'unicamp': UniRegexValidator(
        r'^([a-zA-Z\.-_]+@([a-zA-Z-_]+\.)*unicamp\.br)$',
        "Email inválido para {0}"
    ),
    'pucc': UniRegexValidator(
        r'^[a-zA-Z\.-_]+@puccampinas\.edu\.br$',
        "Email inválido para {0}"
    ),
    'usp': UniRegexValidator(
        r'^([a-zA-Z\.-_]+@([a-zA-Z-_]+\.)*usp\.br)$',
        "Email inválido para {0}"
    ),
    'ifsp': UniRegexValidator(
        r'^[a-zA-Z\.-_]+@ifsp\.edu\.br$',
        "Email inválido para {0}"
    )
}

UNIVERSITY_ID_VALIDATORS = {
    'unicamp': UniRegexValidator(
        r'^\d{5,7}$',
        "RA inválido para {0}"
    ),
    'pucc': UniRegexValidator(
        r'^\d{8}$',
        "RA inválido para {0}"
    ),
    'usp': UniRegexValidator(
        r'^\d{4,10}$',
        "RA inválido para {0}"
    ),
    'ifsp': UniRegexValidator(
        r'^[a-zA-Z]{2}\d{6}$',
        "RA inválido para {0}"
    )
}


class Profile(models.Model):
    """Basic profile information
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    birthday = models.DateField('Data de aniversário')
    gender = models.CharField(
        'Gênero',
        max_length=10,
        choices=GENDER_CHOICES
    )
    phone = PhoneNumberField(
        'Celular',
        help_text="Usado para contato"
    )

    def __str__(self):
        return f"Profile de {self.user}"


class Student(models.Model):
    """Information about the user as a student
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    university = models.CharField(
        'Sua universidades',
        max_length=100,
        choices=UNIVERSITY_CHOICES
    )
    university_email = models.EmailField(
        'Email acadêmico',
        max_length=100
    )
    university_id = models.CharField(
        'ID acadêmica (RA, etc)',
        max_length=30
    )
    enroll_year = models.IntegerField(
        'Ano de ingresso',
        help_text="Ano que você entrou na universidade",
        validators=[
            MaxValueValidator(timezone.now().year),
            MinValueValidator(timezone.now().year - 20)
        ]
    )
    course = models.CharField('Curso', max_length=100)

    def __str__(self):
        return f"Student de {self.user}"


class Driver(models.Model):
    """Information about the user as a driver
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    car_make = models.CharField(
        'Marca do carro',
        max_length=50
    )
    car_model = models.CharField(
        'Modelo do carro',
        max_length=50
    )
    car_color = models.CharField(
        'Cor do carro',
        max_length=30
    )
    likes_pets = models.CharField(
        'Curte animais de estimação',
        choices=PET_CHOICES,
        max_length=30,
        blank=True
    )
    likes_smoking = models.CharField(
        'Curte fumar',
        choices=SMOKING_CHOICES,
        max_length=30,
        blank=True
    )
    likes_music = models.CharField(
        'Curte música',
        choices=MUSIC_CHOICES,
        max_length=30,
        blank=True
    )
    likes_talking = models.CharField(
        'Curte conversar',
        choices=TALKING_CHOICES,
        max_length=30,
        blank=True
    )

    def notify_new_passenger(self, passenger):
        if passenger.status == 'pending':
            trips_webhooks.DriverNewPassengerPendingWebhook(passenger).send()
        else:
            trips_webhooks.DriverNewPassengerApprovedWebhook(passenger).send()

    def notify_passenger_give_up(self, passenger):
        trips_webhooks.DriverPassengerGiveUpWebhook(passenger).send()

    def __str__(self):
        return f"Driver de {self.user}"


class Preferences(models.Model):
    """Whether the user would like to receive emails about stuff
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    updates_notifications = models.BooleanField(
        'Atualizações em caronas e alarmes',
        default=True
    )
    ratings_notifications = models.BooleanField(
        'Avaliações feitas para você',
        default=True
    )
    news_notifications = models.BooleanField(
        'Novidades e notícias do Unicaronas',
        default=True
    )

    def __str__(self):
        return f"Preferences de {self.user}"
