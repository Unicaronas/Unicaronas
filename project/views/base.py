from django.views import generic


class Index(generic.TemplateView):
    template_name = 'project/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['inverted'] = 'inverted'
        return context


class BecomeDev(generic.TemplateView):
    template_name = 'project/become_dev.html'


class TermsAndConditions(generic.TemplateView):
    template_name = 'project/terms_and_conditions.html'


class PrivacyPolicy(generic.TemplateView):
    template_name = 'project/privacy_policy.html'
