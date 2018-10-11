from django.contrib.auth.models import User
from django.db import models
from oauth2_provider.settings import oauth2_settings


class ApplicationRating(models.Model):
    user = models.ForeignKey(
        User,
        related_name='application_ratings',
        on_delete=models.CASCADE
    )
    application = models.ForeignKey(
        oauth2_settings.APPLICATION_MODEL,
        related_name='ratings',
        on_delete=models.CASCADE
    )

    rating = models.BooleanField()
