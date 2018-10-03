from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.


class FacebookGroup(models.Model):
    # Group admin
    user = models.ForeignKey(
        User,
        related_name='facebook_groups',
        on_delete=models.SET_NULL,
        null=True
    )

    # Facebook app info
    client_id = models.CharField(max_length=100)
    client_secret = models.TextField()

    # Group info
    name = models.CharField(max_length=100)
    group_id = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # Token info
    token = models.TextField(blank=True)
    expires = models.DateTimeField(auto_now_add=True)

    def update_token(self, token):
        self.token = token
        self.expires = timezone.now() + timedelta(days=60)
        self.save()

    def days_until_expire(self):
        return (self.expires - timezone.now()).days

    @property
    def is_expired(self):
        return self.days_until_expire() < 0

    @property
    def is_close_to_expire(self):
        return self.days_until_expire() < 30
