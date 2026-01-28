from django.db import models
from django.core.exceptions import ValidationError


class TravelProject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)

    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def update_completion_status(self):
        """
        Mark project as completed if all places are visited
        """
        places = self.places.all()
        if places.exists() and not places.filter(visited=False).exists():
            self.is_completed = True
        else:
            self.is_completed = False
        self.save(update_fields=["is_completed"])

    def clean(self):
        """
        Prevent deleting project if any place is visited
        """
        if self.pk and self.places.filter(visited=True).exists():
            raise ValidationError(
                "Cannot delete project with visited places."
            )

    def delete(self, *args, **kwargs):
        self.clean()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class ProjectPlace(models.Model):
    project = models.ForeignKey(
        TravelProject,
        related_name="places",
        on_delete=models.CASCADE
    )

    external_id = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    visited = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "external_id")
        ordering = ["created_at"]

    def clean(self):
        """
        Enforce max 10 places per project
        """
        if not self.pk and self.project.places.count() >= 10:
            raise ValidationError(
                "A project cannot have more than 10 places."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Update project completion status after save
        self.project.update_completion_status()

    def __str__(self):
        return f"{self.title or 'Place'} ({self.external_id})"
