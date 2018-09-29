from django.views.generic.base import ContextMixin
from django.http import HttpResponseRedirect


class MultiFormMixin(ContextMixin):

    form_classes = {}
    prefixes = {}
    success_urls = {}
    grouped_forms = {}

    initial = {}
    prefix = None
    success_url = None

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes, form_names=None, bind_all=False):
        return dict([(key, self._create_form(key, klass, (form_names and key in form_names) or bind_all))
                     for key, klass in form_classes.items()])

    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = {}
        kwargs.update({'initial': self.get_initial(form_name)})
        kwargs.update({'prefix': self.get_prefix(form_name)})

        if bind_form:
            kwargs.update(self._bind_form_data())

        return kwargs

    def forms_valid(self, forms=None, form_name=None):
        form_valid_method = '%s_form_valid' % form_name
        if hasattr(self, form_valid_method):
            if forms.get(form_name):
                return getattr(self, form_valid_method)(forms[form_name])
            else:
                return getattr(self, form_valid_method)(*[forms[form] for form in self.grouped_forms[form_name]])
        else:
            return HttpResponseRedirect(self.get_success_url(form_name))

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_initial(self, form_name):
        initial_method = 'get_%s_initial' % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def get_prefix(self, form_name):
        return self.prefixes.get(form_name, self.prefix)

    def get_success_url(self, form_name=None):
        return self.success_urls.get(form_name, self.success_url)

    def _create_form(self, form_name, klass, bind_form):
        form_kwargs = self.get_form_kwargs(form_name, bind_form)
        form_create_method = 'create_%s_form' % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def _bind_form_data(self):
        if self.request.method in ('POST', 'PUT'):
            return{'data': self.request.POST,
                   'files': self.request.FILES, }
        return {}


class MultiModelFormMixin(MultiFormMixin):

    def get_form_kwargs(self, form_name, bind_form=False):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs(form_name, bind_form)
        instance_method = 'get_%s_instance' % form_name
        if hasattr(self, instance_method):
            kwargs.update({'instance': getattr(self, instance_method)()})
        return kwargs
