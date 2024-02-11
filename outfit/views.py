from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from closet.models import ClosetClothes
from user.models import Profile
from .models import Outfit, OutfitClothes
from django.db import transaction
from django.db.models import Case, When, IntegerField

def adding_outfits(request, ids):
    if len(ids) != 0:
        outfit = Outfit.objects.create(user_id=request.user.id, name="Default name")
        for item in ids:
            outfit.clothes.add(ClosetClothes.objects.get(clothes_id=item))
        outfit.save()

@login_required
def store_location(request):
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Update user's location in the profile
        user_profile = Profile.objects.get(user=request.user)
        user_profile.location = f"{latitude},{longitude}"
        try:
            user_profile.save()  # Save the changes
        except Exception as e:
            print(f"Error saving location: {e}")
            # If there's an error, render the get_location.html template with latitude and longitude
            return render(request, "get_location.html", {"lat": latitude, "long": longitude})

        return redirect("home")  # Redirect to profile after successful save
    else:
        # Handle GET request
        return render(request, "get_location.html")

@login_required
def increment(request):
    items_ids = request.session.get("suggested_items", [])
    suggested_items = ClosetClothes.objects.filter(clothes_id__in=items_ids)
    with transaction.atomic():
        for item in suggested_items:
            item.worn_count += 1
            item.save()
        adding_outfits(request,items_ids)
    return redirect("home")

@login_required
def all_outfits(request):
    outfits = Outfit.objects.filter(user=request.user).order_by("-add_date")
    return render(request, "all_outfits.html", {"outfits": outfits})



@login_required
def outfit_detail(request, outfit_id):
    outfit_name = Outfit.objects.get(outfit_id=outfit_id)
    outfit = OutfitClothes.objects.filter(outfit_id=outfit_id)
    clothes_ids = outfit.values_list("clothes_id", flat=True)

    # Define custom ordering based on category and item_type
    custom_order = Case(
        When(category='top', then=Case(
            When(subcategory='t-shirt', then=1),
            default=0
        )),
        When(category='bottom', then=1),
        When(category='shoes', then=2),
        default=3,  # For any other category not specified, set it to a higher value
        output_field=IntegerField()
    )

    images = ClosetClothes.objects.filter(clothes_id__in=clothes_ids).order_by(custom_order)
    return render(request, "display_outfit.html", {"images": images, "outfit": outfit_name})
