from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
import oauth2_provider.views as oauth2_views
from oauth2_provider.urls import management_urlpatterns
from django.conf import settings
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('application', views.ApplicationViewset)

urlpatterns = router.urls

app_name = 'oauth2_provider'

# OAuth2 provider endpoints
urlpatterns += [
    path('authorize/', views.CustomAuthorizationView.as_view(), name="authorize"),
    path('token/', oauth2_views.TokenView.as_view(), name="token"),

    path('logout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),

    path('debug_token/', views.DebugToken.as_view(), name="debug_base"),
    path('debug_token/<str:input_token>/', views.DebugToken.as_view(), name="debug"),
]

if settings.DEBUG:
    # OAuth2 Token Management endpoints
    urlpatterns += [
        path('applications/', oauth2_views.ApplicationList.as_view(), name="list"),
        path('applications/register/', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        path('applications/<int:pk>/', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        path('applications/<int:pk>/delete/', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        path('applications/<int:pk>/update/', oauth2_views.ApplicationUpdate.as_view(), name="update"),
        path('management/', include((management_urlpatterns, 'oauth2_provider'))),
        path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
    ]

    # OAuth local API consumer
    urlpatterns += [
        path('consumer/', TemplateView.as_view(template_name='oauth/consumer.html'))
    ]
