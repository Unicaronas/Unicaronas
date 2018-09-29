from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelform_factory
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms as django_forms
from django.contrib.auth.models import User
from project.generics import MultiModelFormsView
from .forms2 import UniversityForm
from .models import Profile, Driver, Preferences
# Create your views here.


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_data/profile.html'


class ProfileEdit(LoginRequiredMixin, MultiModelFormsView):
    template_name = 'user_data/profile_edit.html'
    success_url = reverse_lazy('profile_edit')
    form_classes = {
        'name': modelform_factory(User, fields=['first_name', 'last_name']),
        'profile': modelform_factory(Profile, exclude=['user']),
        'university': UniversityForm,
        'driver': modelform_factory(Driver, fields='__all__', widgets={'user': django_forms.HiddenInput()}),
        'notifications': modelform_factory(Preferences, exclude=['user'])
    }
    grouped_forms = {
        'basic': ['name', 'profile']
    }

    def get_name_instance(self):
        return self.request.user

    def get_profile_instance(self):
        return self.request.user.profile

    def get_university_instance(self):
        return self.request.user.student

    def get_notifications_instance(self):
        return self.request.user.preferences

    def get_driver_instance(self):
        if Driver.objects.filter(user=self.request.user).exists():
            return Driver.objects.get(user=self.request.user)
        return None

    def basic_form_valid(self, *forms):
        for form in forms:
            form.save()
        return super().forms_valid()

    def university_form_valid(self, form):
        form.save()
        return super().forms_valid()

    def notifications_form_valid(self, form):
        form.save()
        return super().forms_valid()

    def driver_form_valid(self, form):
        form.fields['user'] = self.request.user
        form.save()
        return super().forms_valid()

    def get_driver_initial(self):
        return {'user': self.request.user}

    def forms_valid(self, forms, form_name):
        messages.add_message(self.request, messages.SUCCESS, "Informações salvas")
        return super().forms_valid(forms, form_name)

    def forms_invalid(self, forms):
        messages.add_message(self.request, messages.ERROR, "Opa, algo de errado aconteceu!")
        return super().forms_invalid(forms)
