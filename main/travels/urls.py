from rest_framework import routers
from django.urls import path, include
from .views import TravelProjectViewSet, ProjectPlaceViewSet

router = routers.DefaultRouter()
router.register(r'projects', TravelProjectViewSet)
router.register(r'places', ProjectPlaceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]