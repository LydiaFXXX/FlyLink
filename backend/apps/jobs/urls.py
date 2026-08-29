from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostViewSet, JobApplicationViewSet

router = DefaultRouter()
router.register('posts', JobPostViewSet, basename='job-posts')
router.register('applications', JobApplicationViewSet, basename='job-applications')

urlpatterns = [
    path('', include(router.urls)),
]
