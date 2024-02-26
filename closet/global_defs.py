from django.shortcuts import get_object_or_404
from closet.models import ClosetClothes, User_Cloths
from django.db.models import Case, When, IntegerField, Count


class ClosetImageManager:
    def __init__(self, request):
        self.request = request
        self.custom_order = Case(
            When(
                category="top",
                then=Case(When(subcategory="t-shirt", then=1), default=0),
            ),
            When(category="bottom", then=1),
            When(category="shoes", then=2),
            default=3,
            output_field=IntegerField(),
        )

    def get_images(self, is_active=True, **kwargs):
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
        return queryset.values_list("user_cloths__id", "image")

    def images(self, **kwargs):
        return self.get_images(is_active=True, **kwargs)

    def images_restore(self, **kwargs):
        return self.get_images(is_active=False, **kwargs)

    def images_outfit(self, ids, **kwargs):
        try:
            items_list = []
            for i in ids:
                user_cloths = get_object_or_404(User_Cloths, pk=i)
                closet_clothes = get_object_or_404(ClosetClothes, pk=user_cloths.cloths_id)
                items_list.append((i, closet_clothes.image))
            return items_list
        except ClosetClothes.DoesNotExist:
            # Handle the case where no matching objects are found
            return []


class ManageParameters:
    def __init__(self, request):
        self.request = request

    def get_objects(self, model, key):
        queryset = model.objects.filter(pk=key)
        return queryset

    def get_object(self, model, **kwargs):
        one_object = get_object_or_404(model, **kwargs)
        return one_object

    def change_par(self, model, check=None, **kwargs):
        objects = self.get_objects(model, check)
        for obj in objects:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
