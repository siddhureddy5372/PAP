from django.db import models
from django.contrib.auth.models import User


def user_profile_path(instance, filename):
    # This function defines the folder structure for user-uploaded images
    return f'profile_pics/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(blank=True, max_length=40, null=True)
    last_name = models.CharField(blank=True, max_length=40, null=True)
    gender = models.CharField(blank=True, max_length=40, null=True)
    dob = models.CharField(blank=True, max_length=40, null=True)
    location = models.CharField(blank=True, max_length=254, null=True)
    Profile_image = models.ImageField(upload_to=user_profile_path,null = True)