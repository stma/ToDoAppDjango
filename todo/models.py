from django.db import models
from django.urls import reverse
from django.conf import settings


class ToDo(models.Model):
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    private = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Teendok'

    def get_absolute_url(self):
        return reverse('todo_details', args=[str(self.id)])

    def __str__(self):
        return f'[{"X" if self.finished_at else " "}] {self.title}: {str(self.desc)[:10]}... by {self.author and self.author.username} ({self.created_at})'
