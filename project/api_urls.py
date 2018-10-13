from django.urls import path, include


app_name = 'api'

v1_0_api_urlpatterns = [
    path('user/', include('user_data.api.versions.v1_0.urls')),
    path('trips/', include('trips.api.versions.v1_0.urls')),
    path('alarms/', include('alarms.api.versions.v1_0.urls')),
]

urlpatterns = [
    path('v1.0/', include((v1_0_api_urlpatterns, 'api'), namespace='v1.0')),
]
