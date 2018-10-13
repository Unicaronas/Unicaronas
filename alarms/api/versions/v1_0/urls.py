from rest_framework.routers import DefaultRouter
from .views import AlarmViewset

router = DefaultRouter()
# Alarm enpoints
router.register('', AlarmViewset, base_name='alarms')

urlpatterns = router.urls
