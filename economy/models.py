from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Sticker(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    created_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='media')
    quantity = models.IntegerField(default = 1)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class TradeRequest(models.Model):
    requested_sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, related_name='requested')
    requested_quantity = models.IntegerField(default = 1)
    given_sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, related_name='given')
    given_quantity = models.IntegerField(default = 1)
    message = models.TextField(default="Hey, I want to make a trade.")

