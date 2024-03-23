from closet.models import ClosetClothes
from django.db.models import Case, When, IntegerField, Count
from django.db.models import Q
from django.core.cache import cache

class ClosetImageManager:
    """
    Class for managing images and caching.

    Attributes:
        request: HTTP request object.
        custom_order: Defines custom ordering for clothing items.
    """
    def __init__(self, request):
        self.request = request
        # To keep clothes in order by category using Case
        self.custom_order = Case(
            When(
                category="top",
                then=Case(
                    When(Q(subcategory="t-shirts") | Q(subcategory="t-shirt"), then=1),
                    default=0,
                ),
            ),
            When(category="bottom", then=2),
            When(category="shoes", then=3),
            default=3,
            output_field=IntegerField(),
        )

    def get_images_outfit(self, ids):
        """
        Get images of specified clothing items from cache.

        Args:
            ids: IDs of the clothing items to retrieve.

        Returns:
            List of tuples containing (id, image_url) of specified clothing items.
        """
        cache_key = f"{self.request.user.id}_clothes"
        cached_data = cache.get(cache_key)
        if cached_data:
            filtered_objects = [
                (item["id"], item["image"]) for item in cached_data if item["id"] in ids
            ]
            return filtered_objects
        else:
            return None

    def get_images(self, is_active=True, update=False, laundry=False, **kwargs):
        """
        Method to retrieve images based on parameters and update cache if required.

        Args:
            is_active: Flag to indicate if the clothing items are active.
            update: Flag to indicate if cache needs to be updated.
            laundry: Flag to indicate if laundry items are requested.
            **kwargs: Additional filtering parameters.

        Returns:
            List of tuples containing (id, image_url) of clothing items.
        """
        cache_key = f"{self.request.user.id}_clothes"
        if not update:
            cached_data = cache.get(cache_key)
            if cached_data:
                if not laundry:
                    print("FROM Cache closet")
                    # Extract (id,image_url) from data 
                    extracted_data = [
                        (item["id"], item["image"]) for item in cached_data
                    ]
                    return extracted_data
                else:
                    # Filter cloths wiht worn_count more that 3.
                    objects = list(
                        filter(lambda obj: obj["worn_count"] > 3, cached_data)
                    )
                    # Extract (id,image_url) from data 
                    extracted_data = [(item["id"], item["image"]) for item in objects]
                    return extracted_data
                
        queryset = (
            ClosetClothes.objects.filter(
                user_cloths__user=self.request.user, user_cloths__is_active=is_active
            )
            .annotate(num_connections=Count("user_cloths"))
            .filter(
                num_connections__gt=0,
                **kwargs,  # Pass additional keyword arguments to filter()
            )
            .order_by(self.custom_order)  # Order cloths by category with custom_order
            .prefetch_related("user_cloths")
        )
        # Return this list with all cloths (id,image_url)
        queryset_values = list(queryset.values_list("user_cloths__id", "image"))
        # Convert queryset values to a list of tuples
        query_list = list(
            queryset.values_list(
                "user_cloths__id",
                "image",
                "brand",
                "model",
                "color",
                "category",
                "subcategory",
                "user_cloths__worn_count",
            )
        )

        # Convert the list of tuples to a list of dictionaries with descriptive keys
        queryset_dict_list = [
            {
                "id": item[0],
                "image": item[1],
                "brand": item[2],
                "model": item[3],
                "color": item[4],
                "category": item[5],
                "subcategory": item[6],
                "worn_count": item[7],
            }
            for item in query_list
        ]

        # Delete existing cache data and store the formatted data in cache with a timeout of 300 seconds (5 minutes)
        cache.delete(cache_key)
        cache.set(cache_key, queryset_dict_list, timeout=300)
        # Return the original queryset values
        return queryset_values



    def images_restore(self, **kwargs):
        """
        Method to retrieve images of restoreable items.

        Args:
            **kwargs: Additional filtering parameters.

        Returns:
            List of tuples containing (id, image_url) of restoreable clothing items.
        """
        queryset = (
            ClosetClothes.objects.filter(
                user_cloths__user=self.request.user, user_cloths__is_active=False
            )
            .annotate(num_connections=Count("user_cloths"))
            .filter(
                num_connections__gt=0,
                **kwargs,  # Pass additional keyword arguments to filter()
            )
            .order_by("-user_cloths__deleted_date")
            .prefetch_related("user_cloths")
        )
        queryset_values = list(queryset.values_list("user_cloths__id", "image"))
        return queryset_values

class ManageParameters:
    """
    Class for managing parameters of clothing items.

    Attributes:
        request: HTTP request object.
    """
    def __init__(self, request):
        self.request = request

    def get_objects(self, model, key):
        """
        Get objects from database based on model and key.

        Args:
            model: Django model to query.
            key: Primary key of the object.

        Returns:
            Queryset of the specified objects.
        """
        queryset = model.objects.filter(pk=key)
        return queryset

    def change_par(self, model, check=None, **kwargs):
        """
        Method to change parameters of specified objects.

        Args:
            model: Django model to query.
            check: Primary key of the object.
            **kwargs: Parameters to update.

        Returns:
            None
        """
        objects = self.get_objects(model, check)
        for obj in objects:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
