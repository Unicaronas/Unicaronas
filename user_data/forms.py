from django import forms
import re
from allauth.account.forms import SignupForm, LoginForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from allauth.account.forms import app_settings
from .models import UNIVERSITY_EMAIL_VALIDATORS, UNIVERSITY_ID_VALIDATORS


class CustomSignupForm(SignupForm):

    username = forms.CharField(label="ID acadêmica (RA, etc)",
                               min_length=app_settings.USERNAME_MIN_LENGTH,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          '123456',
                                          'autofocus': 'autofocus'}))
    email = forms.EmailField(
        label="Email universitário",
        widget=forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'Seu email na sua universidade'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email acadêmico"

    def clean(self):
        cleaned_data = super().clean()
        university = cleaned_data['university']

        # Validate university email
        email = cleaned_data.get('email')
        if not email:
            # If no email was provided, validation failed. Return
            return
        UNIVERSITY_EMAIL_VALIDATORS[university](email, university)
        cleaned_data['university_email'] = email.lower()

        # Validate university ID
        uid = cleaned_data.get('username')
        if not uid:
            # If no username was provided, validation failed. Return
            return
        UNIVERSITY_ID_VALIDATORS[university](uid, university)
        cleaned_data['university_id'] = uid.lower()
        return cleaned_data


class CustomSocialSignupForm(SocialSignupForm):

    username = forms.CharField(label="ID acadêmica (RA, etc)",
                               min_length=app_settings.USERNAME_MIN_LENGTH,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          '123456',
                                          'autofocus': 'autofocus'}))
    email = forms.EmailField(
        label="Email universitário",
        widget=forms.TextInput(
            attrs={'type': 'email',
                   'placeholder': 'Seu email na sua universidade'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email acadêmico"

    def clean(self):
        cleaned_data = super().clean()
        university = cleaned_data['university']

        # Validate university email
        email = cleaned_data.get('email')
        if not email:
            # If no email was provided, validation failed. Return
            return
        UNIVERSITY_EMAIL_VALIDATORS[university](email, university)
        cleaned_data['university_email'] = email.lower()

        # Validate university ID
        uid = cleaned_data.get('username')
        if not uid:
            # If no username was provided, validation failed. Return
            return
        UNIVERSITY_ID_VALIDATORS[university](uid, university)
        cleaned_data['university_id'] = uid.lower()
        return cleaned_data


class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        login_widget = forms.TextInput(attrs={'placeholder':
                                              'Seu RA, etc',
                                              'autofocus': 'autofocus'})
        login_field = forms.CharField(
            label="ID universitário",
            widget=login_widget)
        self.fields["login"] = login_field
