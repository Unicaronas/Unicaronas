from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


GENDER_CHOICES = (
    ('male', 'Masculino'),
    ('female', 'Feminino'),
    ('other', 'Outro'),
    ('na', 'Prefiro não dizer')
)

TALKING_CHOICES = (
    (0, 'Gosto de paisagens'),
    (1, 'Às vezes curto conversar'),
    (2, 'Adoro conversar!')
)

SMOKING_CHOICES = (
    (0, 'Cigarro não, por favor'),
    (1, 'Às vezes permito fumar'),
    (2, 'Cigarro não me incomoda')
)

PET_CHOICES = (
    (0, 'Animais não, por favor'),
    (1, 'Depende do animal'),
    (2, 'Adoro animais!')
)

MUSIC_CHOICES = (
    (0, 'Curto silêncio'),
    (1, 'Depende da música'),
    (2, 'Adoro música!')
)

UNIVERSITY_CHOICES = (
    ('unicamp', 'Unicamp'),
)

UNIVERSITY_EMAIL_VALIDATORS = {
    'unicamp': r'^(([a-zA-Z]\d{5,7}@dac.unicamp.br)|([a-zA-Z]\d{5,7}@g.unicamp.br))$'
}

UNIVERSITY_ID_VALIDATORS = {
    'unicamp': r'^\d{5,7}$'
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
    phone = models.CharField(
        'Celular',
        max_length=20,
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
    likes_pets = models.IntegerField(
        'Curte animais de estimação',
        choices=PET_CHOICES,
        default=0
    )
    likes_smoking = models.IntegerField(
        'Curte fumar',
        choices=SMOKING_CHOICES,
        default=0
    )
    likes_music = models.IntegerField(
        'Curte música',
        choices=MUSIC_CHOICES,
        default=0
    )
    likes_talking = models.IntegerField(
        'Curte conversar',
        choices=TALKING_CHOICES,
        default=0
    )

    def notify_new_passenger(self, passenger):
        """Passenger is an User"""
        raise NotImplementedError("Implementar envio de mensagem para motorista")

    def notify_passenger_give_up(self, passenger):
        """Passenger is an User"""
        raise NotImplementedError("Implementar envio de mensagem para motorista")

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
