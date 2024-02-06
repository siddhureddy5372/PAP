from django.db import models
from django.contrib.auth.models import User
from closet.models import ClosetClothes



class Outfit(models.Model):
    outfit_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    clothes = models.ManyToManyField(ClosetClothes, through='OutfitClothes')

class OutfitClothes(models.Model):
    id = models.AutoField(primary_key=True)
    clothes = models.ForeignKey(ClosetClothes, on_delete=models.CASCADE)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE)
