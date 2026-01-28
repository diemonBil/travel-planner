from rest_framework import serializers
from .models import TravelProject, ProjectPlace, ProjectPlaceAssignment


class ProjectPlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectPlace
        fields = ['id', 'external_id', 'title']


# Серіалізатор для місця в контексті проєкту
class ProjectPlaceAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    external_id = serializers.IntegerField(source='place.external_id', read_only=True)
    title = serializers.CharField(source='place.title', read_only=True)

    class Meta:
        model = ProjectPlaceAssignment
        fields = ['id', 'external_id', 'title', 'notes', 'visited']
        read_only_fields = ['id', 'external_id', 'title']


class TravelProjectSerializer(serializers.ModelSerializer):
    # Read-only nested field to show assignments
    places = ProjectPlaceAssignmentSerializer(
        source='projectplaceassignment_set',
        many=True,
        read_only=True
    )

    # Write-only field for creating/adding places via external_id
    place_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = TravelProject
        fields = ['id', 'name', 'description', 'start_date', 'is_completed', 'places', 'place_ids']

    def create(self, validated_data):
        place_ids = validated_data.pop('place_ids', [])
        project = TravelProject.objects.create(**validated_data)

        for external_id in place_ids:
            place, _ = ProjectPlace.objects.get_or_create(external_id=external_id)
            ProjectPlaceAssignment.objects.create(project=project, place=place)

        project.update_completion_status()
        return project

    def update(self, instance, validated_data):
        place_ids = validated_data.pop('place_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if place_ids is not None:
            for external_id in place_ids:
                place, _ = ProjectPlace.objects.get_or_create(external_id=external_id)
                ProjectPlaceAssignment.objects.get_or_create(project=instance, place=place)

        instance.update_completion_status()
        return instance
