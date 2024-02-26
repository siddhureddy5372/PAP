from django.db import models
from django.contrib.auth.models import User
from closet.models import User_Cloths
from django.utils import timezone



class Outfit(models.Model):
    outfit_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    clothes = models.ManyToManyField(User_Cloths, through='OutfitClothes')
    add_date = models.DateTimeField(default=timezone.now)

class OutfitClothes(models.Model):
    id = models.AutoField(primary_key=True)
    clothes = models.ForeignKey(User_Cloths, on_delete=models.CASCADE, null=True)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE, null=True)

