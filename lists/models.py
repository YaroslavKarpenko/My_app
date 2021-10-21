from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy


class Project(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    name = models.CharField("Name", max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('home')


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    priority = models.IntegerField()
    content = models.CharField(max_length=2048)
    is_active = models.BooleanField(default=True)
    deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['priority']

    def get_absolute_url(self):
        return reverse_lazy('home')
