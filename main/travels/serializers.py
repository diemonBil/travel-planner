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


class TravelProjectSerializer(serializers.ModelSerializer):
    # Nested serializer for places: now writable
    places = ProjectPlaceAssignmentSerializer(
        source='projectplaceassignment_set', many=True
    )

    class Meta:
        model = TravelProject
        fields = ['id', 'name', 'description', 'start_date', 'is_completed', 'places']

    def update(self, instance, validated_data):
        # Extract nested data for places
        places_data = validated_data.pop('projectplaceassignment_set', [])
        print("places_data", places_data)
        # Update normal project fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nested places
        for place_data in places_data:
            print("sobaka")
            assignment_id = place_data.get('id')
            notes = place_data.get('notes', '')
            visited = place_data.get('visited', False)
            print("assignment_id", assignment_id)
            print("notes", notes)
            print("visited", visited)
            try:
                assignment = ProjectPlaceAssignment.objects.get(id=assignment_id, project=instance)
                assignment.notes = notes
                assignment.visited = visited
                assignment.save()
            except ProjectPlaceAssignment.DoesNotExist:
                continue

        instance.update_completion_status()
        return instance
