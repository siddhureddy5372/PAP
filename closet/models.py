from django.db import models
from django.contrib.auth.models import User


def user_folder_path(instance, filename):
    # This function defines the folder structure for user-uploaded images
    return f'images/{filename}'


class ClosetClothes(models.Model):
    clothes_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=20)
    subcategory = models.CharField(max_length=20)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    image = models.ImageField(upload_to=user_folder_path)
    add_date = models.DateField()
    waterproof = models.IntegerField(default = 0)

    class Meta:
        managed = False
        db_table = 'closet_clothes'

class User_Cloths(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    cloths = models.ForeignKey(ClosetClothes, models.CASCADE, blank=True, null=True)
    deleted_date = models.DateTimeField(blank = True,null = True)
    worn_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'user_cloths'