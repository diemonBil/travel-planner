from rest_framework import serializers
from .models import TravelProject, ProjectPlace


class ProjectPlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectPlace
        fields = ['id', 'external_id', 'title', 'notes', 'visited', 'project']


class TravelProjectSerializer(serializers.ModelSerializer):
    places = ProjectPlaceSerializer(many=True, read_only=True)

    class Meta:
        model = TravelProject
        fields = ['id', 'name', 'description', 'start_date', 'is_completed', 'places']


