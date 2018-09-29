from rest_framework_nested import routers
from .views import DriverTripViewset, DriverPassengerActionsViewset

router = routers.DefaultRouter()
router.register('driver', DriverTripViewset, base_name='driver-trips')

driver_actions = routers.NestedSimpleRouter(router, 'driver', lookup='trip')
driver_actions.register('passengers', DriverPassengerActionsViewset, base_name='driver-trips-passengers')

urlpatterns = router.urls

urlpatterns += driver_actions.urls
