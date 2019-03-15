from django.contrib import admin

from .models import DBResult, Hit


@admin.register(DBResult)
class DBResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'query', 'address', 'address_components', 'point', 'created', 'expires')
    list_filter = ('created', 'expires')


@admin.register(Hit)
class HitAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'result',
        'created',
        'application',
        'user',
        'path_info',
        'full_path_info',
        'method',
        'query_type',
    )
    list_filter = ('created',)
