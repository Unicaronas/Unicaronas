import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from versatileimagefield.fields import VersatileImageField
from oauth2_provider import models as omodels
from oauth2_provider.scopes import get_scopes_backend
from oauth2_provider.settings import oauth2_settings
from project.validators import MaxImageDimensionsValidator, MinImageDimensionsValidator, SquareImageValidator, CustomURLValidator


from .utils import Cipher
from .exceptions import InvalidScopedUserId

# Create your models here.


@property
def scoped_user_id(self):
    return Application.get_scoped_user_id(self.application, self.user)


omodels.AbstractAccessToken.add_to_class('scoped_user_id', scoped_user_id)


def get_logo_path(instance, file_name):
    return f"app_logos/{instance.user.student.university_id}/{instance.client_id}.{file_name.split('.')[-1]}"


class Application(omodels.AbstractApplication):
    """Modified OAuth Application model (Client)

    Implements the application scopes as fields.

    Scopes are selected during the creation of the client
    and are presented to the user. The user, then, can
    allow or not certain scopes, generating more restrictive
    tokens.

    Clients are given a list of available scopes during creation and editing
    based on the client's user permission group

    Fields:
    * :attr:`application_id` The app identifier
    * :attr:`client_id` The client identifier issued to the client during the
                        registration process as described in :rfc:`2.2`
    * :attr:`user` ref to a Django user
    * :attr:`redirect_uris` The list of allowed redirect uri. The string
                            consists of valid URLs separated by space
    * :attr:`client_type` Client type as described in :rfc:`2.1`
    * :attr:`authorization_grant_type` Authorization flows available to the
                                       Application
    * :attr:`client_secret` Confidential secret issued to the client during
                            the registration process as described in :rfc:`2.2`
    * :attr:`name` Friendly name for the Application
    * :attr:`scope` Space-separated scope names
    * :attr:`plataform` Plataform that the application runs on
    * :attr:`description` Application description that will be displayed during user permission request
    """

    GRANT_AUTHORIZATION_CODE = "authorization-code"
    GRANT_IMPLICIT = "implicit"
    GRANT_TYPES = (
        (GRANT_AUTHORIZATION_CODE, "Authorization code"),
        (GRANT_IMPLICIT, "Implicit"),
    )
    PLATFORM_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Website'),
        ('facebook', 'Facebook'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('windows', 'Windows'),
        ('mac', 'MacOS'),
        ('linux', 'Linux')
    )
    CLIENT_CONFIDENTIAL = 'confidential'
    CLIENT_PUBLIC = 'public'
    CLIENT_TYPE_CHOICES = (
        (CLIENT_CONFIDENTIAL, 'Confidential'),
        (CLIENT_PUBLIC, 'Public')
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    client_type = models.CharField(choices=CLIENT_TYPE_CHOICES, max_length=32, default=CLIENT_CONFIDENTIAL)
    authorization_grant_type = models.CharField(
        max_length=32, choices=GRANT_TYPES, default=GRANT_AUTHORIZATION_CODE
    )
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='web')
    scope = models.TextField(blank=True, help_text="Requested scopes, space separated")

    website = models.URLField(blank=True, help_text="App's website or download page")
    published = models.BooleanField(default=False, help_text="Whether or not your app is published")
    published_past = models.BooleanField(default=False, help_text="Whether or not the app has been published before")
    logo = VersatileImageField(
        "App's logo",
        blank=True,
        upload_to=get_logo_path,
        validators=[MinImageDimensionsValidator(512, 512), MaxImageDimensionsValidator(1024, 1024), SquareImageValidator()]
    )
    webhook_url = models.URLField(validators=[CustomURLValidator()], blank=True)

    @property
    def requested_scopes(self):
        """
        Returns a set of requested scope names (as keys) with their descriptions (as values)
        """
        return set(oauth2_settings._DEFAULT_SCOPES + self.scope.split(' '))

    @property
    def requested_scopes_dict(self):
        all_scopes = get_scopes_backend().get_all_scopes()
        app_scopes = list(self.requested_scopes)
        return {name: desc for name, desc in all_scopes.items() if name in app_scopes}

    @property
    def redirect_uris_list(self):
        return self.redirect_uris.split()

    def approved_scopes(self, user):
        """
        Returns the set of approved scopes by the user
        Represents the set that contains all scopes ever approved by the user to this app
        """
        tokens = omodels.get_access_token_model().objects.filter(
            user=user,
            application=self
        )
        scopes = {}
        for token in tokens:
            for key, value in token.scopes.items():
                scopes[key] = value
        return scopes

    def get_users(self):
        return User.objects.filter(oauth2_provider_accesstoken__application=self).distinct()

    class Meta(omodels.AbstractApplication.Meta):
        swappable = "OAUTH2_PROVIDER_APPLICATION_MODEL"
        ordering = ['-id']

    @classmethod
    def get_scoped_user_cipher(cls, application=None, user=None):
        if application is not None and user is not None:
            # Used to make sure that the same app, user pair always has the same scoped id
            iv_seed = str((user.id + application.id) * settings.SECRET_PRIME)
            iv = hashlib.sha256(iv_seed.encode()).digest()
        else:
            iv = None
        key = settings.SECRET_KEY
        return Cipher(key, iv)

    @classmethod
    def get_scoped_user_id(cls, application, user):
        """
        Takes and app and a user and generates a
        reversible and secure scoped user id.

        Can be of any method:
        - Database-based
        - Crypto-based

        The current method is crypto based and uses Fernet
        to generate a secure user_id
        """

        # Assert that only apps are hashed
        assert isinstance(application, omodels.get_application_model())
        # Assert that only users are hashed
        assert isinstance(user, User)
        # The key is used is the secret key digested into a sha256 hash
        c = cls.get_scoped_user_cipher(application, user)
        return c.encrypt(f"{application.id}:==:{user.id}")

    @classmethod
    def recover_scoped_user_id(cls, scoped_user_id, get_app=False):
        """
        Takes a scoped user id and returns the user and the app

        If no valid user is found, return None
        """
        try:
            c = cls.get_scoped_user_cipher()
            app_id, user_id = c.decrypt(scoped_user_id).split(':==:')
            user = User.objects.get(id=user_id)
            app = Application.objects.get(id=app_id)
        except Exception as e:
            raise InvalidScopedUserId(e)
        if get_app:
            return app, user
        return user


@receiver(post_save, sender=Application, dispatch_uid="refresh_app_logos")
def refresh_app_logos(sender, instance, **kwargs):
    instance.logo.delete_all_created_images()


@receiver(models.signals.post_delete, sender=Application, dispatch_uid="delete_app_logos")
def delete_app_logos(sender, instance, **kwargs):
    # Deletes Image Renditions
    instance.logo.delete_all_created_images()
    # Deletes Original Image
    instance.logo.delete(save=False)
