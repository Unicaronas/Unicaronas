from django.urls import path
from .views import FacebookGroupTokenBegin, FacebookGroupTokenUpdate

app_name = 'third_parties'

urlpatterns = [
    path('facebook/groups/redirect/<int:id>/', FacebookGroupTokenBegin.as_view(), name='fb_group_redirect'),
    path('facebook/groups/callback/', FacebookGroupTokenUpdate.as_view(), name='fb_group_callback'),
]
