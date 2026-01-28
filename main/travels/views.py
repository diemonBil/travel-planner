from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import TravelProject, ProjectPlace, ProjectPlaceAssignment
from .serializers import TravelProjectSerializer, ProjectPlaceAssignmentSerializer, ProjectPlaceSerializer
import requests


class TravelProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel projects.
    Supports listing, creating, updating, and deleting projects.
    Places are handled via ProjectPlaceAssignment for per-project notes and visited status.
    """
    queryset = TravelProject.objects.all()
    serializer_class = TravelProjectSerializer

    def create(self, request, *args, **kwargs):
        # Ensure at least one place is provided when creating a project
        if not request.data.get('new_places'):
            return Response(
                {"error": "A project must have at least one place"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Prevent deletion if any place in the project is marked as visited
        project = self.get_object()
        if project.projectplaceassignment_set.filter(visited=True).exists():
            return Response(
                {"error": "Cannot delete project with visited places"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ProjectPlaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing standalone places.
    Supports validation of external_id via Art Institute of Chicago API.
    """
    queryset = ProjectPlace.objects.all()
    serializer_class = ProjectPlaceSerializer

    def create(self, request, *args, **kwargs):
        external_id = request.data.get('external_id')

        if not external_id:
            return Response({"error": "external_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the place exists via Art Institute API
        r = requests.get(
            "https://api.artic.edu/api/v1/artworks",
            params={"ids": external_id}
        )
        data = r.json().get("data", [])

        if not data:
            return Response(
                {"error": f"Place with id {external_id} not found in Art Institute API"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optionally populate the title from API
        title = data[0].get("title", "")
        request.data["title"] = title

        return super().create(request, *args, **kwargs)