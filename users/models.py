from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model) :
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fullname = models.CharField(max_length=10)
    image = models.ImageField(upload_to='profile/', default='default.png')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs) :
    if created :
        Profile.objects.create(user=instance)