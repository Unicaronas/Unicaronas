from django.contrib import admin


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
        'logo',
    )
    list_filter = (
        'user',
        'skip_authorization',
        'created',
        'updated',
        'published',
    )
    search_fields = ('name',)
