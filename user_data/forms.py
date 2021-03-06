from django import forms
from django.core.validators import FileExtensionValidator
from allauth.account.forms import SignupForm, LoginForm, set_form_field_order, get_adapter
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from allauth.account.forms import app_settings
from .fields import SquareCroppieField
from .models import UNIVERSITY_EMAIL_VALIDATORS, UNIVERSITY_ID_VALIDATORS, UNIVERSITY_CHOICES, Profile


class CustomSignupForm(SignupForm):

    username = forms.CharField(
        label="ID acadêmica (RA, etc)",
        min_length=app_settings.USERNAME_MIN_LENGTH,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'placeholder':
                '123456',
                'autofocus': 'autofocus',
                'data-validation': 'required length',
                'data-validation-length': 'max30'
            }
        ))
    email = forms.EmailField(
        label="Email universitário",
        widget=forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'meu@email.com',
                   'data-validation': 'required email'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email acadêmico"
        self.fields['email2'].label = "Email acadêmico (novamente)"
        self.fields['email2'].widget = forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'meu@email.com',
                   'data-validation': 'required email confirmation',
                   'data-validation-confirm': 'email'})
        self.fields['password1'].widget = forms.TextInput(
            attrs={'type': 'password',
                   'data-validation': 'required strength',
                   'data-validation-strength': '2'})
        self.fields['password2'].widget = forms.TextInput(
            attrs={'type': 'password',
                   'data-validation': 'required confirmation',
                   'data-validation-confirm': 'password1'})
        set_form_field_order(self, ['university'])

    def clean_username(self):
        username = super().clean_username()
        university = self.cleaned_data['university']
        value = f"{username}@{university}"
        value = get_adapter().clean_username(value)
        return value

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        university = cleaned_data['university']

        # Validate university email
        email = cleaned_data.get('email')
        if not email:
            # If no email was provided, validation failed. Return
            return
        UNIVERSITY_EMAIL_VALIDATORS[university](
            university, email, **cleaned_data)
        cleaned_data['university_email'] = email.lower()

        # Validate university ID
        uid = '@'.join(cleaned_data.get('username').split('@')[:-1])
        if not uid:
            # If no username was provided, validation failed. Return
            return
        UNIVERSITY_ID_VALIDATORS[university](university, uid, **cleaned_data)
        cleaned_data['university_id'] = uid.lower()
        return cleaned_data


class CustomSocialSignupForm(SocialSignupForm):

    username = forms.CharField(
        label="ID acadêmica (RA, etc)",
        min_length=app_settings.USERNAME_MIN_LENGTH,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'placeholder':
                '123456',
                'autofocus': 'autofocus',
                'data-validation': 'required length',
                'data-validation-length': 'max30'
            }
        ))
    email = forms.EmailField(
        label="Email universitário",
        widget=forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'meu@email.com',
                   'data-validation': 'required email'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email acadêmico"
        self.fields['email2'].label = "Email acadêmico (novamente)"
        self.fields['email2'].widget = forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'meu@email.com',
                   'data-validation': 'required email confirmation',
                   'data-validation-confirm': 'email'})
        set_form_field_order(self, ['university'])

    def clean_username(self):
        username = super().clean_username()
        university = self.cleaned_data['university']
        value = f"{username}@{university}"
        value = get_adapter().clean_username(value)
        return value

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        university = cleaned_data['university']

        # Validate university email
        email = cleaned_data.get('email')
        if not email:
            # If no email was provided, validation failed. Return
            return
        UNIVERSITY_EMAIL_VALIDATORS[university](
            university, email, **cleaned_data)
        cleaned_data['university_email'] = email.lower()

        # Validate university ID
        uid = '@'.join(cleaned_data.get('username').split('@')[:-1])
        if not uid:
            # If no username was provided, validation failed. Return
            return
        UNIVERSITY_ID_VALIDATORS[university](university, uid, **cleaned_data)
        cleaned_data['university_id'] = uid.lower()
        return cleaned_data


class CustomLoginForm(LoginForm):

    university = forms.ChoiceField(
        required=True,
        choices=UNIVERSITY_CHOICES,
        label="Sua universidade",
        widget=forms.Select(
            attrs={
                "css": "ui fluid search selection dropdown"
            }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        login_widget = forms.TextInput(
            attrs={
                'placeholder':
                'Seu RA, etc',
                'autofocus': 'autofocus'
            }
        )
        login_field = forms.CharField(
            label="ID universitário",
            widget=login_widget)
        self.fields["login"] = login_field
        set_form_field_order(self, ['university'])

    def clean_login(self):
        login = super().clean_login()
        university = self.cleaned_data['university']
        return f"{login}@{university}"


class ProfileForm(forms.ModelForm):
    picture = SquareCroppieField(
        label="Foto de perfil",
        options={
            "showZoomer": True,
            "viewport": {
                "width": 256,
                "height": 256,
                "type": 'circle'
            },
            "initialZoomMin": True,
            "maxZoomedCropWidth": 257,
            "minZoomedCropWidth": 2048
        },
        required=False
    )

    class Meta:
        model = Profile
        exclude = ('user',)
