from django import forms
from user_data.models import MissingUniversity


class MissingUniversityForm(forms.ModelForm):
    class Meta:
        model = MissingUniversity
        fields = '__all__'
