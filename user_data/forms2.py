from datetime import datetime
from django import forms
from django.core.validators import FileExtensionValidator
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from .models import Profile, Student, Driver, Preferences, StudentProof
from .models import GENDER_CHOICES, PET_CHOICES, SMOKING_CHOICES, TALKING_CHOICES, MUSIC_CHOICES, UNIVERSITY_CHOICES
from phonenumber_field.formfields import PhoneNumberField


class ExtraSignupFields(forms.Form):
    # Basic
    first_name = forms.CharField(
        label="Primeiro nome",
        widget=forms.TextInput(
            attrs={'data-validation': 'required'})
    )
    last_name = forms.CharField(
        label="Sobrenome",
        widget=forms.TextInput(
            attrs={'data-validation': 'required'})
    )

    # Profile
    birthday = forms.DateField(
        label="Data de aniversário",
        widget=forms.TextInput(
            attrs={
                'data-validation': 'required birthdate',
                'data-validation-format': 'dd/mm/yyyy'})
    )
    gender = forms.ChoiceField(
        label="Gênero",
        choices=GENDER_CHOICES
    )
    phone = PhoneNumberField(
        label="Celular",
        widget=forms.TextInput(
            attrs={'data-validation': 'required brphone'})
    )

    # Student
    university = forms.ChoiceField(
        label="Sua universidade",
        choices=UNIVERSITY_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'ui search selection dropdown'
            }
        )
    )
    university_id = forms.CharField(required=False, widget=forms.HiddenInput())
    university_email = forms.CharField(
        required=False, widget=forms.HiddenInput())
    enroll_year = forms.IntegerField(
        label="Ano de ingresso",
        widget=forms.TextInput(
            attrs={
                'data-validation': 'number',
                'data-validation-allowing': f"range[{datetime.now().year - 25};{datetime.now().year}]"
            })
    )
    course = forms.CharField(
        label="Curso",
        widget=forms.TextInput(
            attrs={'data-validation': 'required'})
    )

    # Driver info
    car_make = forms.CharField(
        label="Marca do carro",
        required=False,
        widget=forms.TextInput(
            attrs={
                'data-validation': 'required',
                'data-validation-depends-on': 'is_driver'
            })
    )
    car_model = forms.CharField(
        label="Modelo do carro",
        required=False,
        widget=forms.TextInput(
            attrs={
                'data-validation': 'required',
                'data-validation-depends-on': 'is_driver'
            })
    )
    car_color = forms.CharField(
        label="Cor do carro",
        required=False,
        widget=forms.TextInput(
            attrs={
                'data-validation': 'required',
                'data-validation-depends-on': 'is_driver'
            })
    )

    # Preferences
    likes_pets = forms.ChoiceField(
        label="Curte animais de estimação",
        required=False,
        choices=PET_CHOICES
    )
    likes_smoking = forms.ChoiceField(
        label="Curte fumar",
        required=False,
        choices=SMOKING_CHOICES
    )
    likes_music = forms.ChoiceField(
        label="Curte música",
        required=False,
        choices=MUSIC_CHOICES
    )
    likes_talking = forms.ChoiceField(
        label="Curte conversar",
        required=False,
        choices=TALKING_CHOICES
    )
    student_proof = forms.FileField(
        label='Certificado de matrícula/diploma/foto da carteirinha/etc',
        allow_empty_file=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])],
        required=False,
        widget=forms.FileInput(
            attrs={
                'data-validation': 'required size mime',
                'data-validation-max-size': '5M',
                'data-validation-allowing': 'jpg, png, pdf'
            })
    )
    contact_email = forms.EmailField(
        label='Email para contato após verificação',
        required=False,
        widget=forms.EmailInput(
            attrs={
                'data-validation': 'required email',
            })
    )

    # Captcha
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(attrs={"data-callback": "captchaSpottedCallback"}))

    def clean(self):
        cleaned_data = self.cleaned_data

        if cleaned_data['car_make'] or cleaned_data['car_model'] or cleaned_data['car_color']:
            if not cleaned_data['car_make']:
                raise forms.ValidationError(
                    {'car_make': ['Marca do carro necessária se você for motorista']})
            if not cleaned_data['car_model']:
                raise forms.ValidationError(
                    {'car_model': ['Modelo do carro necessário se você for motorista']})
            if not cleaned_data['car_color']:
                raise forms.ValidationError(
                    {'car_color': ['Cor do carro necessária se você for motorista']})
        return cleaned_data

    def signup(self, request, user):
        cleaned_data = self.cleaned_data
        user.save()

        # Process profile
        profile = Profile(
            user=user,
            birthday=cleaned_data['birthday'],
            gender=cleaned_data['gender'],
            phone=cleaned_data['phone']
        )
        profile.save()

        # Process student
        student = Student(
            user=user,
            university=cleaned_data['university'],
            university_email=cleaned_data['university_email'],
            university_id=cleaned_data['university_id'],
            enroll_year=cleaned_data['enroll_year'],
            course=cleaned_data['course']
        )
        student.save()

        # Process driver
        if cleaned_data['car_make']:
            driver = Driver(
                user=user,
                car_make=cleaned_data['car_make'],
                car_model=cleaned_data['car_model'],
                car_color=cleaned_data['car_color'],
                likes_pets=cleaned_data['likes_pets'],
                likes_smoking=cleaned_data['likes_smoking'],
                likes_music=cleaned_data['likes_music'],
                likes_talking=cleaned_data['likes_talking'],
            )
            driver.save()

        # Process Notifications
        preferences = Preferences(user=user)
        preferences.save()

        contact_email = cleaned_data.get('contact_email', cleaned_data['university_email'])

        # Process Student Proof submission
        if cleaned_data.get('student_proof', None):
            StudentProof.create(student, contact_email, cleaned_data['student_proof'])


class UniversityForm(forms.ModelForm):

    university = forms.ChoiceField(
        label="Sua universidade",
        choices=UNIVERSITY_CHOICES,
        disabled=True,
        widget=forms.Select(attrs={'readonly': True})
    )
    university_id = forms.CharField(
        label="ID acadêmica (RA, etc)",
        disabled=True,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    university_email = forms.CharField(
        label="Email acadêmico",
        disabled=True,
        widget=forms.TextInput(attrs={'readonly': True})
    )

    class Meta:
        model = Student
        exclude = ['user']
        readonly_fields = ['university', 'university_id', 'university_email']
