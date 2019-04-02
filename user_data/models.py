import requests
from django.db import models
from django.conf import settings
from django.core.mail import mail_admins
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from allauth.account.models import EmailAddress
from project.utils import import_current_version_module
from .validators import UniRegexValidator, FallbackUniRegexValidator
from .mailing import approved_student_proof_email
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
    ('usp', 'USP'),
    ('unesp', 'Unesp'),
    ('unifesp', 'Unifesp'),
    ('pucc', 'PUC-Campinas'),
    ('ifsp', 'IFSP'),
    ('facamp', 'FACAMP')
)

UNIVERSITY_EMAIL_VALIDATORS = {
    'unicamp': UniRegexValidator(
        r'^([a-zA-Z\.-_]+@([a-zA-Z-_]+\.)*unicamp\.br)$',
        "Email inválido para {0}"
    ),
    'usp': UniRegexValidator(
        r'^([a-zA-Z\.-_]+@([a-zA-Z-_]+\.)*usp\.br)$',
        "Email inválido para {0}"
    ),
    'unesp': UniRegexValidator(
        r'^[a-zA-Z\.-_]+@unesp\.br$',
        "Email inválido para {0}"
    ),
    'unifesp': UniRegexValidator(
        r'^[a-zA-Z\.-_]+@unifesp\.br$',
        "Email inválido para {0}"
    ),
    'pucc': UniRegexValidator(
        r'^[a-zA-Z\.-_]+@puccampinas\.edu\.br$',
        "Email inválido para {0}"
    ),
    'ifsp': UniRegexValidator(
        r'^[a-zA-Z\.-_]+@ifsp\.edu\.br$',
        "Email inválido para {0}"
    ),
    'facamp': FallbackUniRegexValidator(
        r'a^',
        "Alunos da {0} deve submeter seu atestado de matrícula/diploma"
    )
}

UNIVERSITY_ID_VALIDATORS = {
    'unicamp': UniRegexValidator(
        r'^\d{5,7}$',
        "RA inválido para {0}"
    ),
    'usp': UniRegexValidator(
        r'^\d{4,10}$',
        "RA inválido para {0}"
    ),
    'unesp': UniRegexValidator(
        r'^\d{7,11}$',
        "RA inválido para {0}"
    ),
    'unifesp': UniRegexValidator(
        r'^\d{7,11}$',
        "RA inválido para {0}"
    ),
    'pucc': UniRegexValidator(
        r'^\d{8}$',
        "RA inválido para {0}"
    ),
    'ifsp': UniRegexValidator(
        r'^[a-zA-Z]{2}\d{6}$',
        "RA inválido para {0}"
    ),
    'facamp': UniRegexValidator(
        r'^\d{7,12}$',
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
            MinValueValidator(timezone.now().year - 25)
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


class MissingUniversity(models.Model):
    """Universities that are missing from the API"""

    name = models.CharField('Seu nome', max_length=50)
    email = models.EmailField('Seu email para contato')
    university_name = models.CharField(
        'Nome ou sigla da universidade/faculdade', max_length=50)
    university_id = models.CharField('ID acadêmica (RA, etc)', max_length=50)
    university_email = models.EmailField('Email acadêmico')


def filename(instance, filename):
    return f"uploads/student_proofs/{get_random_string()}.pdf"


class StudentProof(models.Model):
    """Proof of student enrollment"""

    pending_status = 'pending'
    approved_status = 'approved'
    denied_status = 'denied'

    status_choices = (
        (pending_status, 'Pendente'),
        (approved_status, 'Aprovado'),
        (denied_status, 'Negado')
    )

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )
    proof = models.FileField(upload_to=filename, validators=[
                             FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])])
    proof_scan_url = models.URLField(blank=True)
    proof_scan_id = models.CharField(blank=True, max_length=300)
    contact_email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default=pending_status, choices=status_choices, max_length=20)

    @classmethod
    def create(cls, student, email, proof):
        sp = cls(
            student=student,
            contact_email=email,
            proof=proof
        )
        sp.save()
        if settings.VIRUS_TOTAL_API_KEY:
            # Perform virus total scan
            result = requests.post('https://www.virustotal.com/vtapi/v2/url/scan', {
                "apikey": settings.VIRUS_TOTAL_API_KEY,
                "url": sp.proof.url
            })
            if result.status_code == requests.codes.ok:
                sp.proof_scan_url = result.json()['permalink']
                sp.proof_scan_id = result.json()['scan_id']
                sp.save()
        mail_admins(
            subject='Novo pedido de aprovação de usuário',
            message='Um novo usuário se cadastrou e pediu revisão manual de seu status de verificação'
        )

    @property
    def scan_results(self):
        if self.proof_scan_url == '':
            return 'Indisponível'
        result = requests.get('https://www.virustotal.com/vtapi/v2/url/report', {
            "apikey": settings.VIRUS_TOTAL_API_KEY,
            "resource": self.proof_scan_id
        })
        if result.status_code == requests.codes.ok and result.json()['response_code'] == 1:
            data = result.json()
            if data['positives'] == 0:
                return 'Tudo ok'
            return f"{data['positives']}/{data['total']} positivos"
        return 'Erro'

    def approve(self):
        email_address, created = EmailAddress.objects.get_or_create(
            user=self.student.user, email__iexact=self.contact_email, defaults={
                "email": self.contact_email}
        )
        email_address.set_as_primary()
        emails = EmailAddress.objects.filter(user=self.student.user)
        emails.update(verified=True)
        approved_student_proof_email(self.student.user)
        self.status = self.approved_status
        self.save()

    def deny(self):
        emails = EmailAddress.objects.filter(user=self.student.user)
        emails.update(verified=False)
        self.status = self.denied_status
        self.save()
