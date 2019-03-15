from django.contrib.auth.models import User
from django.contrib.gis.db import models
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from oauth2_provider.settings import oauth2_settings
# Create your models here.


def get_default_expire_days():
    return getattr(settings, 'DEFAULT_DB_SEARCH_EXPIRE_DAYS', 60)


def get_default_expire():
    return timezone.now() + timedelta(days=get_default_expire_days())


class DBResult(models.Model):
    """
    Long lived search result
    Prevents redundant Google Geocoding hits
    """
    query = models.CharField(
        "Pesquisa original",
        max_length=500
    )
    address = models.TextField(
        "Enderço completo da pesquisa",
        max_length=200
    )
    point = models.PointField("Coordenadas da pesquisa")
    address_components = JSONField(
        default=list,
        null=True,
        verbose_name='Componentes do endereço'
    )
    created = models.DateTimeField(
        "Data de adesão da pesquisa",
        auto_now_add=True
    )
    expires = models.DateTimeField(default=get_default_expire)

    def extend_expire(self, days=0):
        """Extend expiration date"""
        self.expires = get_default_expire()
        self.save()

    def hit(self, term):
        """Add a single hit"""
        self.extend_expire()
        request = term.request
        app = getattr(request.auth, 'application', None)
        user = request.user if request.user.is_authenticated else None
        path_info = request.path_info
        full_path_info = request.get_full_path_info()
        method = request.method
        query_type = term.query_type
        Hit.objects.create(
            result=self,
            application=app,
            user=user,
            path_info=path_info,
            full_path_info=full_path_info,
            method=method,
            query_type=query_type
        )

    @classmethod
    def result_update_or_create(cls, result):
        query = result.query
        address = result.address
        point = result.point
        address_components = result.address_components
        cls.objects.update_or_create(
            query=query,
            defaults={
                "address": address,
                "point": point,
                "expires": get_default_expire(),
                "address_components": address_components
            }
        )


class Hit(models.Model):
    """Representation of a database hit"""
    # DBResult of the hit
    result = models.ForeignKey(
        DBResult,
        related_name='hits',
        on_delete=models.CASCADE
    )
    # When the hit happened
    created = models.DateTimeField(auto_now_add=True)
    # Application that issued the hit, if any
    application = models.ForeignKey(
        oauth2_settings.APPLICATION_MODEL,
        related_name='search_hits',
        on_delete=models.SET_NULL,
        null=True
    )
    # User that issued the hit, if any
    user = models.ForeignKey(
        User,
        related_name='search_hits',
        on_delete=models.SET_NULL,
        null=True
    )
    # /path/of/request/
    path_info = models.CharField(max_length=200)
    # /path/of/request/?query=strings
    full_path_info = models.TextField()
    # GET, POST, etc
    method = models.CharField(max_length=10)
    # Query type (origin, destination)
    query_type = models.CharField(max_length=20)
