import requests
from django.db import models
from django.core.exceptions import ValidationError


class ProjectPlaceAssignment(models.Model):
    project = models.ForeignKey('TravelProject', on_delete=models.CASCADE)
    place = models.ForeignKey('ProjectPlace', on_delete=models.CASCADE)
    visited = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('project', 'place')


class ProjectPlace(models.Model):
    external_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, blank=True)  # тягнемо з API
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # якщо title порожній, тягнемо з API
        if not self.title:
            r = requests.get(f'https://api.artic.edu/api/v1/artworks', params={'ids': self.external_id})
            data = r.json().get('data', [])
            if data:
                self.title = data[0].get('title', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title or 'Place'} ({self.external_id})"


class TravelProject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    places = models.ManyToManyField(
        'ProjectPlace',
        through='ProjectPlaceAssignment',
        related_name='projects'
    )

    def clean(self):
        if self.pk and self.projectplaceassignment_set.filter(visited=True).exists():
            raise ValidationError("Cannot delete project with visited places.")

    def delete(self, *args, **kwargs):
        self.clean()
        super().delete(*args, **kwargs)

    def update_completion_status(self):
        """
        Mark project as completed if all assigned places are visited.
        Checks visited status from ProjectPlaceAssignment (through table).
        """
        self.is_completed = not self.projectplaceassignment_set.filter(visited=False).exists()
        self.save(update_fields=["is_completed"])

    def add_places(self, places):
        """Add places to project with max 10 validation"""
        if self.places.count() + len(places) > 10:
            raise ValidationError("A project cannot have more than 10 places.")
        self.places.add(*places)
        self.update_completion_status()

    def __str__(self):
        return self.name
