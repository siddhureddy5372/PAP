from django.core.cache import cache
from user.models import Profile
from .global_defs import ClosetImageManager
from outfit.outfit_gen import suggest_outfit
from django.core.exceptions import ObjectDoesNotExist

class Caching():
    """
    Class for caching user-specific data.

    Attributes:
        request: HTTP request object.
    """
    def __init__(self,request):
        self.request = request

    def get_cloth(self,cloth_id):
        """
        Get details of a clothing item from cache.

        Args:
            id: ID of the clothing item to retrieve.

        Returns:
            Details of the specified clothing item.
        """
        cache_key = f"{self.request.user.id}_clothes"
        cache_data = cache.get(cache_key)
        if cache_data:
            desired_objects = list(filter(lambda obj: obj["id"] == cloth_id, cache_data))
            return desired_objects[0]


    def get_profile(self,type_):
        """
        Get or update user profile data in cache.

        Args:
            type_: Type of operation, either "get" or "update".

        Returns:
            User profile data.
        """
        cache_key = f"{self.request.user.id}_profile"
        if type_ == "get":
            if cache.get(cache_key):
                return cache.get(cache_key)
        try:
            user_id = self.request.user.id
            user_profile = Profile.objects.get(user=user_id)
        except ObjectDoesNotExist:
            return None

        if type_ == "update":
            cache.delete(cache_key)
        cache.set(cache_key,user_profile,timeout=1000)
        return user_profile
        

class UpdateCache():
    """
    Class for updating cache data.

    Attributes:
        request: HTTP request object.
    """
    def __init__(self,request):
        self.request = request

    def setup(self):
        """
        Setup cache by updating user profile, suggesting outfits, and refreshing image cache.
        """
        global_def = ClosetImageManager(self.request)
        manage = Caching(self.request)

        manage.get_profile("update")
        suggest_outfit(self.request)
        global_def.get_images(update=True)
