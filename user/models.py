from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_profile_path(instance, filename):
    # This function defines the folder structure for user-uploaded images
    return f'images/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(blank=True, max_length=40, null=True)
    last_name = models.CharField(blank=True, max_length=40, null=True)
    gender = models.CharField(blank=True, max_length=40, null=True)
    dob = models.CharField(blank=True, max_length=40, null=True)
    location = models.CharField(blank=True, max_length=254, null=True)
    Profile_image = models.ImageField(upload_to=user_profile_path)


    


