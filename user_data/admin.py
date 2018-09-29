from django.contrib import admin
from .models import Profile, Student, Driver, Preferences
# Register your models here.


admin.site.register(Profile)
admin.site.register(Student)
admin.site.register(Driver)
admin.site.register(Preferences)
