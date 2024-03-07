from django.shortcuts import get_object_or_404
from closet.models import ClosetClothes
from django.db.models import Case, When, IntegerField, Count
from django.db.models import Q
from django.core.cache import cache

class ClosetImageManager:
    def __init__(self, request):
        self.request = request
        self.custom_order = Case(
            When(
                category="top",
                then = Case(When(Q(subcategory="t-shirts") | Q(subcategory="t-shirt"), then=1), default=0),
            ),
            When(category="bottom", then=2),
            When(category="shoes", then=3),
            default=3,
            output_field=IntegerField(),
        )
    
    def get_images(self, is_active=True,update = False, **kwargs):
        cache_key = f"{self.request.user.id}_clothes"
        if not update:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                print(cached_data)
                extracted_data = [(item[0], item[1]) for item in cached_data]
                return extracted_data
        print("FROM DB")
        queryset = (
            ClosetClothes.objects.filter(
                user_cloths__user=self.request.user, user_cloths__is_active=is_active
            )
            .annotate(num_connections=Count("user_cloths"))
            .filter(
                num_connections__gt=0,
                **kwargs  # Pass additional keyword arguments to filter()
            )
            .order_by(self.custom_order)
            .prefetch_related('user_cloths')  
        )
        queryset_values = list(queryset.values_list("user_cloths__id", "image"))
        query_list = list(queryset.values_list("user_cloths__id", "image","brand","brand","user_cloths__worn_count"))
        # Delete the existing images
        cache.delete(cache_key)
        # Store the data in cache with a timeout of 300 seconds (5 minutes)
        cache.set(cache_key, query_list, timeout=300)
        return queryset_values
    
    def images(self, **kwargs):
        return self.get_images(is_active=True, **kwargs)

    def images_restore(self, **kwargs):
        return self.get_images(is_active=False, **kwargs)



class ManageParameters:
    def __init__(self, request):
        self.request = request

    def get_objects(self, model, key):
        queryset = model.objects.filter(pk=key)
        return queryset
    
    def change_par(self, model, check=None, **kwargs):
        objects = self.get_objects(model, check)
        for obj in objects:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
