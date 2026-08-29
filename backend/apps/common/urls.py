from django.urls import path
from .views import platform_stats

urlpatterns = [
    path('stats/', platform_stats),
]
