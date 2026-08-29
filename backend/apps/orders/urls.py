from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet

router = DefaultRouter()
router.register('', WorkOrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
