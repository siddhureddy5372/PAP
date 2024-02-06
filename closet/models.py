import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

def user_folder_path(instance, filename):
    # This function defines the folder structure for user-uploaded images
    return f'user_{instance.user.id}/{filename}'

class ClosetClothes(models.Model):
    clothes_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=20)
    subcategory = models.CharField(max_length=20)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    image = models.ImageField(upload_to=user_folder_path)
    add_date = models.DateTimeField()
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    worn_count = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'closet_clothes'

# Connect the pre_delete signal to a function to delete user folders
@receiver(pre_delete, sender=User)
def delete_user_folders(sender, instance, **kwargs):
    # Get the user folder path and delete it
    user_folder_path = f'media/user_{instance.id}'
    if os.path.exists(user_folder_path):
        os.rmdir(user_folder_path)
