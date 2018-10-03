from django.contrib import admin

from .models import FacebookGroup


@admin.register(FacebookGroup)
class FacebookGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'client_id',
        'client_secret',
        'name',
        'updated',
        'created',
        'token',
        'expires',
    )
    list_filter = ('user', 'updated', 'created', 'expires')
    search_fields = ('name',)
