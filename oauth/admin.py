from django.contrib import admin

from .models import ApplicationRating


class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client_id',
        'user',
        'redirect_uris',
        'client_secret',
        'skip_authorization',
        'created',
        'updated',
        'name',
        'description',
        'client_type',
        'authorization_grant_type',
        'platform',
        'scope',
        'website',
        'published',
        'published_past',
        'logo',
        'webhook_url',
    )
    list_filter = (
        'user',
        'skip_authorization',
        'created',
        'updated',
        'published',
        'published_past',
    )
    search_fields = ('name',)


@admin.register(ApplicationRating)
class ApplicationRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'application', 'rating')
    list_filter = ('user', 'application', 'rating')
