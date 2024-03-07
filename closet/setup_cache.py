from django.core.cache import cache
from user.models import Profile
from django.db.models import Count
from .models import ClosetClothes

class Caching():
    def __init__(self,request):
        self.request = request

    def get_cloth(self,id):
        cache_key = f"{self.request.user.id}_clothes"
        cache_data = cache.get(cache_key)
        if cache_data:
            desired_objects = list(filter(lambda obj: obj[0] == id, cache_data))
            print(desired_objects[0])
            return desired_objects[0]


    def get_profile(self,type_):
        cache_key = f"{self.request.user.id}_profile"
        if type_ == "get":
            if cache.get(cache_key):
                print("FROM CACHE")
                return cache.get(cache_key)
        user_id = self.request.user.id
        user_profile = Profile.objects.get(user=user_id)
        print("FROM DB")
        if type_ == "update":
            cache.delete(cache_key)
        cache.set(cache_key,user_profile,timeout=300)
        return user_profile
        

class UpdateCache():
    def __init__(self,request):
        self.request = request


    def store_clothes(self):
        cache_key = f"{self.request.user.id}_clothes"
        queryset = (
            ClosetClothes.objects.filter(
                user_cloths__user=self.request.user, user_cloths__is_active=True
            )
            .annotate(num_connections=Count("user_cloths"))
            .filter(
                num_connections__gt=0, # Pass additional keyword arguments to filter()
            )
            .order_by(self.custom_order)
            .prefetch_related('user_cloths')  
        )
        queryset_values = list(queryset)
        # Delete the existing images
        cache.delete(cache_key)
        # Store the data in cache with a timeout of 300 seconds (5 minutes)
        cache.set(cache_key, queryset_values, timeout=300)
    