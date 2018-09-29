from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from oauth2_provider.models import get_application_model, get_refresh_token_model, get_access_token_model
from oauth.forms import ApplicationForm


class DetailApplications(generic.DetailView):
    model = get_application_model()
    template_name = 'project/detail_apps.html'

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(published=True)


class ListApplications(generic.ListView):
    model = get_application_model()
    paginate_by = 10
    template_name = 'project/list_apps.html'
    context_object_name = 'apps'

    def get_queryset(self):
        search = self.request.GET.get('search', False)
        published_apps = self.model.objects.filter(published=True)
        if not search:
            return published_apps
        return published_apps.filter(Q(name__icontains=search) | Q(description__icontains=search))


class ConnectedApplications(LoginRequiredMixin, generic.ListView):
    model = get_application_model()
    paginate_by = 10
    template_name = 'project/connected_apps.html'
    context_object_name = 'apps'

    def get_queryset(self):
        search = self.request.GET.get('search', False)
        connected_apps = self.model.objects.filter(accesstoken__user=self.request.user).distinct()
        if not search:
            return connected_apps
        return connected_apps.filter(Q(name__icontains=search) | Q(description__icontains=search))


class RevokeAccess(LoginRequiredMixin, generic.View):
    """Revoke access to an application"""

    def post(self, request):
        app_id = request.POST.get('application_id', False)
        app = get_application_model().objects.filter(id=app_id)
        if app.exists():
            app = app.first()
            refresh_tokens = get_refresh_token_model().objects.filter(
                user=request.user,
                application=app
            )
            for token in refresh_tokens:
                token.revoke()
            access_tokens = get_access_token_model().objects.filter(
                user=request.user,
                application=app
            )
            for token in access_tokens:
                token.revoke()
            messages.add_message(request, messages.SUCCESS, f'Acesso de {app.name} revogado com sucesso')
        return redirect('apps_connected')


class MyApplications(LoginRequiredMixin, generic.ListView):
    model = get_application_model()
    paginate_by = 10
    template_name = 'project/list_my_apps.html'
    context_object_name = 'apps'

    def get_queryset(self):
        search = self.request.GET.get('search', False)
        my_apps = self.model.objects.filter(user=self.request.user)
        if not search:
            return my_apps
        return my_apps.filter(Q(name__icontains=search) | Q(description__icontains=search))


class TogglePublish(LoginRequiredMixin, generic.View):

    def post(self, request):
        app_id = request.POST.get('application_id', False)
        app = get_application_model().objects.filter(id=app_id)
        if app.exists() and app.first().user == self.request.user:
            app = app.first()
            message = f"{app.name} publicado com sucesso!"
            if app.published:
                message = f"{app.name} despublicado com sucesso!"
            app.published = not app.published
            app.save()
            messages.add_message(request, messages.SUCCESS, message)
        return redirect('apps_my')


class CreateApp(LoginRequiredMixin, generic.CreateView):
    form_class = ApplicationForm
    template_name = 'project/create_app.html'
    success_url = reverse_lazy('apps_my')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, f"{form.cleaned_data['name']} criado!")
        return super().form_valid(form)


class UpdateApp(LoginRequiredMixin, generic.UpdateView):
    model = get_application_model()
    form_class = ApplicationForm
    template_name = 'project/update_app.html'
    success_url = reverse_lazy('apps_my')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.initial['scope'] = form.initial['scope'].split()
        return form

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, f"{form.cleaned_data['name']} atualizado!")
        return super().form_valid(form)


class DeleteApp(LoginRequiredMixin, generic.DeleteView):
    model = get_application_model()
    success_url = reverse_lazy('apps_my')

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.add_message(request, messages.WARNING, "Aplicativo apagado!")
        return response
