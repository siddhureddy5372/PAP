from closet.models import ClosetClothes
from django.db.models import Case, When, IntegerField
from django.db.models import Count



def images(request, **kwargs):
    custom_order = Case(
        When(category='top', then=Case(
            When(subcategory='t-shirt', then=1),
            default=0
        )),
        When(category='bottom', then=1),
        When(category='shoes', then=2),
        default=3,
        output_field=IntegerField()
    )
    # Create a dynamic queryset based on parameters
    queryset = ClosetClothes.objects.filter(
        user_cloths__user=request.user,
        user_cloths__is_active=True
    ).annotate(
        num_connections=Count('user_cloths')
    ).filter(
        num_connections__gt=0,
        **kwargs  # Pass additional keyword arguments to filter()
    ).order_by(custom_order)

    # Return the queryset
    return queryset.values_list(
        'user_cloths__id',
        'image'
    )

def images_restore(request, **kwargs):
    custom_order = Case(
        When(category='top', then=Case(
            When(subcategory='t-shirt', then=1),
            default=0
        )),
        When(category='bottom', then=1),
        When(category='shoes', then=2),
        default=3,
        output_field=IntegerField()
    )
    # Create a dynamic queryset based on parameters
    queryset = ClosetClothes.objects.filter(
        user_cloths__user=request.user,
        user_cloths__is_active=False
    ).annotate(
        num_connections=Count('user_cloths')
    ).filter(
        num_connections__gt=0,
        **kwargs  # Pass additional keyword arguments to filter()
    ).order_by(custom_order)

    # Return the queryset
    return queryset.values_list(
        'user_cloths__id',
        'image'
    )

