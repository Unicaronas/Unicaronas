from oauth2_provider.scopes import SettingsScopes


class CustomSettingsScopes(SettingsScopes):
    """Custom scope

    This works with the custom Application model
    to limit applications to just a few scopes.
    """

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        return application.requested_scopes.copy()

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        return super().get_default_scopes(application, request, *args, **kwargs).copy()

    def get_all_scopes(self):
        return super().get_all_scopes().copy()
