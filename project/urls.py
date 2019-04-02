"""unicaronas_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar
from user_data.views import ProfileView, ProfileEdit
from watchman import views as watchman_views
from . import views
from .views import Handler404, Handler500

handler404 = Handler404.as_view()
handler500 = Handler500.as_view()


api_urlpatterns = [
    path('api/', include('project.api_urls')),
]

docs_urlpatterns = [
    path('docs/', include('project.docs_urls')),
]

application_patterns = [
    path('applications/', views.ListApplications.as_view(), name='apps_list'),
    path('applications/<int:pk>/', views.DetailApplications.as_view(), name='apps_detail'),
    path('applications/connected/', views.ConnectedApplications.as_view(), name='apps_connected'),
    path('applications/connected/revoke/', views.RevokeAccess.as_view(), name='apps_revoke'),
    path('applications/connected/rate/', views.RateApp.as_view(), name='apps_rate'),
    path('applications/my/', views.MyApplications.as_view(), name='apps_my'),
    path('applications/my/toggle_publish/', views.TogglePublish.as_view(), name='toggle_publish'),
    path('applications/create/', views.CreateApp.as_view(), name='apps_create'),
    path('applications/update/<int:pk>/', views.UpdateApp.as_view(), name='apps_update'),
    path('applications/delete/<int:pk>/', views.DeleteApp.as_view(), name='apps_delete'),
]

admin_patterns = [
    path('admin/', admin.site.urls),
]

account_patterns = [
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('accounts/profile/edit/', ProfileEdit.as_view(), name='profile_edit'),
]

oauth_patterns = [
    path('o/', include('oauth.urls')),
]

third_parties_patterns = [
    path('third_parties/', include('third_parties.urls')),
]

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('terms_and_conditions/', views.TermsAndConditions.as_view(), name='terms_and_conditions'),
    path('privacy_policy/', views.PrivacyPolicy.as_view(), name='privacy_policy'),
    path('what_is_oauth/', views.OAuthHelp.as_view(), name='oauth_help'),
    path('missing_university/', views.MissingUniversity.as_view(), name='missing_university'),
]

urlpatterns += api_urlpatterns
urlpatterns += docs_urlpatterns
urlpatterns += application_patterns
urlpatterns += admin_patterns
urlpatterns += account_patterns
urlpatterns += oauth_patterns
urlpatterns += third_parties_patterns
urlpatterns += [
    path('status/', watchman_views.dashboard, name='watchman-dashboard'),
    path('status/ping', watchman_views.ping, name='watchman-ping'),
]

if settings.SHOW_TOOLBAR_CALLBACK:

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
