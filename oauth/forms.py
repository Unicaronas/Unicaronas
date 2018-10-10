from django import forms
from oauth2_provider import models, scopes
from oauth2_provider.scopes import get_scopes_backend
from versatileimagefield.forms import VersatileImageFormField


class CustomAllowForm(forms.Form):
    """Custom allow form

    When requesting permission from user, this form is showed
    This allows users to select which permissions to give using
    checkboxes
    """
    allow = forms.BooleanField(required=False)
    redirect_uri = forms.CharField(widget=forms.HiddenInput())
    scope = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
        attrs={'class': 'form-check-input'}), required=False)
    scope_choices = forms.CharField(widget=forms.HiddenInput())
    client_id = forms.CharField(widget=forms.HiddenInput())
    state = forms.CharField(required=False, widget=forms.HiddenInput())
    response_type = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = kwargs['initial'].get('scope_choices', '[]')
        if kwargs.get('data', False):
            choices = kwargs['data']['scope_choices']
        self.fields['scope'].choices = eval(choices)

    def clean_scope(self):
        scopes = self.cleaned_data['scope']
        for def_scope in get_scopes_backend().get_default_scopes():
            # Prevent users from removing default scopes
            if def_scope not in scopes:
                scopes.append(def_scope)
        if not scopes and self.cleaned_data['allow']:
            raise forms.ValidationError(
                "Você deve escolher pelo menos uma permissão")
        return ' '.join(scopes)


class ApplicationForm(forms.ModelForm):

    scope = forms.CharField(
        label="Permissões",
        widget=forms.CheckboxSelectMultiple(
            choices=scopes.get_scopes_backend().get_all_scopes().items())
    )

    logo = VersatileImageFormField(label="Logo (opcional)", help_text="Quadrado, entre 512x512 e 1024x1024 px", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.fields['scope'].initial:
            self.fields['scope'].initial = self.fields['scope'].initial.split()

    def clean_scope(self):
        scopes = eval(self.cleaned_data['scope'])
        for def_scope in get_scopes_backend().get_default_scopes():
            if def_scope not in scopes:
                scopes.append(def_scope)
        return ' '.join(scopes)

    class Meta:
        model = models.get_application_model()
        fields = ['name', 'description', 'client_type', 'authorization_grant_type',
                  'platform', 'scope', 'redirect_uris', 'website', 'logo', 'webhook_url']

        labels = {
            'name': 'Nome do aplicativo',
            'description': 'Descrição',
            'client_type': 'Tipo de cliente',
            'authorization_grant_type': 'Tipo de autorização',
            'platform': 'Plataforma',
            'redirect_uris': 'URIs de redirecionamento (uma por linha)',
            'website': 'Página do app/Link para Download (opcional)',
            'logo': 'URL do logo (opcional)',
            'webhook_url': 'URL para receber Webhooks (opcional)',
        }
