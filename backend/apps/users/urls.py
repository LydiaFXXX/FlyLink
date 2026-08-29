from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('pilots', views.PilotProfileViewSet, basename='pilots')
router.register('resumes', views.PilotResumeViewSet, basename='resumes')
router.register('reviews', views.CreditReviewViewSet, basename='reviews')

urlpatterns = [
    path('register/', views.register),
    path('me/', views.me),
    path('', include(router.urls)),
]
