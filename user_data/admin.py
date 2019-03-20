from django.contrib import admin
from .models import Profile, Student, Driver, Preferences, MissingUniversity


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'birthday', 'gender', 'phone')
    list_filter = ('user', 'birthday')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'university',
        'university_email',
        'university_id',
        'enroll_year',
        'course',
    )
    list_filter = ('university',)
    search_fields = ('user', 'university_id',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'car_make',
        'car_model',
        'car_color',
        'likes_pets',
        'likes_smoking',
        'likes_music',
        'likes_talking',
    )
    search_fields = ('user',)


@admin.register(Preferences)
class PreferencesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'updates_notifications',
        'ratings_notifications',
        'news_notifications',
    )
    list_filter = (
        'updates_notifications',
        'ratings_notifications',
        'news_notifications',
    )
    search_fields = ('user',)


@admin.register(MissingUniversity)
class MissingUniversityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'university_name',
        'university_id',
        'university_email'
    )
    list_filter = ('university_name', 'name')
    search_fields = ('name', 'email', 'university_name', )
