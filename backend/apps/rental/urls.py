from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DroneDeviceViewSet, RentalOrderViewSet

router = DefaultRouter()
router.register('devices', DroneDeviceViewSet, basename='devices')
router.register('orders', RentalOrderViewSet, basename='rental-orders')

urlpatterns = [
    path('', include(router.urls)),
]
