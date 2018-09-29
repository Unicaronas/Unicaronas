from django.urls import path
from .views import UserData

app_name = 'user_data'

urlpatterns = [
    path('', UserData.as_view(), name='me'),
]
