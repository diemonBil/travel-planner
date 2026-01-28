from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import TravelProject, ProjectPlace, ProjectPlaceAssignment
from .serializers import TravelProjectSerializer, ProjectPlaceAssignmentSerializer


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
        if not request.data.get('place_ids'):
            return Response(
                {"error": "A project must have at least one place"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(request.data.get('place_ids')) > 10:
            return Response(
                {"error": "A project cannot have more than 10 places"},
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


class ProjectPlaceAssignmentViewSet(viewsets.ViewSet):
    """
    Nested ViewSet for managing places inside a specific travel project.
    """

    def list(self, request, project_pk=None):
        """
        List all places for a given project
        """
        queryset = ProjectPlaceAssignment.objects.filter(project_id=project_pk)
        serializer = ProjectPlaceAssignmentSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, project_pk=None):
        """
        Retrieve a single place within a project
        """
        try:
            assignment = ProjectPlaceAssignment.objects.get(
                id=pk, project_id=project_pk
            )
        except ProjectPlaceAssignment.DoesNotExist:
            return Response(
                {"error": "Place not found in this project"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectPlaceAssignmentSerializer(assignment)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        """
        Add a new place to a project using external_id
        """
        external_id = request.data.get("external_id")
        notes = request.data.get("notes", "")

        if not external_id:
            return Response(
                {"error": "external_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = TravelProject.objects.get(pk=project_pk)

        # Enforce max 10 places per project
        if project.projectplaceassignment_set.count() >= 10:
            return Response(
                {"error": "A project cannot have more than 10 places"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            place, _ = ProjectPlace.objects.get_or_create(
                external_id=external_id
            )
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate place in the same project
        if ProjectPlaceAssignment.objects.filter(
            project=project, place=place
        ).exists():
            return Response(
                {"error": "This place is already added to the project"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment = ProjectPlaceAssignment.objects.create(
            project=project,
            place=place,
            notes=notes,
        )

        project.update_completion_status()

        serializer = ProjectPlaceAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, project_pk=None):
        try:
            assignment = ProjectPlaceAssignment.objects.get(
                id=pk,
                project_id=project_pk
            )
        except ProjectPlaceAssignment.DoesNotExist:
            return Response(
                {"error": "Place not found in this project"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectPlaceAssignmentSerializer(
            assignment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update project completion status
        assignment.project.update_completion_status()

        return Response(serializer.data)

    def destroy(self, request, pk=None, project_pk=None):
        """
        Remove a place from a project.
        A project must always have at least one place.
        """
        try:
            assignment = ProjectPlaceAssignment.objects.get(
                id=pk, project_id=project_pk
            )
        except ProjectPlaceAssignment.DoesNotExist:
            return Response(
                {"error": "Place not found in this project"},
                status=status.HTTP_404_NOT_FOUND,
            )

        project = assignment.project

        # Ensure project has at least one place
        if project.projectplaceassignment_set.count() <= 1:
            return Response(
                {"error": "A project must have at least one place"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment.delete()
        project.update_completion_status()

        return Response(status=status.HTTP_204_NO_CONTENT)
