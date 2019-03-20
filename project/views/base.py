from django.views import generic
from django.contrib import messages
from django.core.mail import mail_admins
from ..forms import MissingUniversityForm


class Index(generic.TemplateView):
    template_name = 'project/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['inverted'] = 'inverted'
        return context


class OAuthHelp(generic.TemplateView):
    template_name = 'project/oauth_help.html'


class TermsAndConditions(generic.TemplateView):
    template_name = 'project/terms_and_conditions.html'


class PrivacyPolicy(generic.TemplateView):
    template_name = 'project/privacy_policy.html'


class MissingUniversity(generic.edit.CreateView):
    template_name = 'project/missing_university.html'
    form_class = MissingUniversityForm
    success_url = '/'

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Sua universidade foi enviada para nossa equipe e será adicionada em breve! Te avisaremos por email quando isso acontecer.'
        )
        mail_admins(
            subject="Universidade submetida",
            message=f"{form.instance.name} acabou de submeter dados da universidade {form.instance.university_name}",
            fail_silently=True
        )
        return super().form_valid(form)
