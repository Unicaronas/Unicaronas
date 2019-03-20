from django.contrib import admin

from .models import Alarm


@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'origin',
        'origin_point',
        'origin_radius',
        'destination',
        'destination_point',
        'destination_radius',
        'price',
        'auto_approve',
        'datetime_lte',
        'datetime_gte',
        'min_seats',
    )
    list_filter = (
        'created',
        'auto_approve',
        'datetime_lte',
        'datetime_gte',
    )
    search_fields = ('origin', 'destination')
