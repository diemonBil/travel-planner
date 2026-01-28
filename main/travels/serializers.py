from rest_framework import serializers
from .models import TravelProject, ProjectPlace


class TravelProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelProject
        fields = ['id', 'external_id', 'name', 'notes', 'visited', 'project']


class ProjectPlaceSerializer(serializers.ModelSerializer):
    places = TravelProjectSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectPlace
        fields = ['id', 'name', 'description', 'start_date', 'completed', 'places']
