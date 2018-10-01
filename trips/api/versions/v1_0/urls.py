from django.urls import path
from rest_framework_nested import routers
from .views import DriverTripViewset, DriverPassengerActionsViewset, SearchTripViewset, PassengerTripViewset, ThirdPartyTripSearchView

router = routers.DefaultRouter()
# Driver endpoints
router.register('driver', DriverTripViewset, base_name='driver-trips')
# Passenger endpoints
router.register('passenger', PassengerTripViewset, base_name='passenger-trips')
# Search endpoints
router.register('local', SearchTripViewset, base_name='search-trips')

# Extra driver actions on passengers
driver_actions = routers.NestedSimpleRouter(router, 'driver', lookup='trip')
driver_actions.register('passengers', DriverPassengerActionsViewset, base_name='driver-trips-passengers')

urlpatterns = router.urls

urlpatterns += [path('external', ThirdPartyTripSearchView.as_view())]

urlpatterns += driver_actions.urls
