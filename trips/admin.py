from django.contrib import admin

from .models import Trip, Passenger


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'origin',
        'origin_point',
        'origin_address_components',
        'destination',
        'destination_point',
        'destination_address_components',
        'price',
        'datetime',
        'max_seats',
        'auto_approve',
        'details',
        'application',
    )
    list_filter = ('created', 'datetime', 'auto_approve')


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'trip', 'status', 'book_time')
    list_filter = ('user', 'trip', 'book_time')
