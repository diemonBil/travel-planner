from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TravelProjectViewSet, ProjectPlaceAssignmentViewSet

router = DefaultRouter()
router.register(r'projects', TravelProjectViewSet, basename='projects')

# Nested routes for places in a project
place_list = ProjectPlaceAssignmentViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

place_detail = ProjectPlaceAssignmentViewSet.as_view({
    'get': 'retrieve',
    'patch': 'update',
    'put': 'update',
    'delete': 'destroy',
})

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:project_pk>/places/', place_list, name='project-places-list'),
    path('projects/<int:project_pk>/places/<int:pk>/', place_detail, name='project-place-detail'),
]