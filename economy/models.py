from django.db import models
from django.utils import timezone
# Create your models here.

class Sticker(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title