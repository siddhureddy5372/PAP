from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from closet.models import ClosetClothes,User_Cloths
from user.models import Profile
from .models import Outfit, OutfitClothes
from django.db import transaction
from django.db.models import Case, When, IntegerField
from django.http import HttpResponseBadRequest

def adding_outfits(request, ids, outfit_name):
    if len(ids) > 2:
        outfit = Outfit.objects.create(user=request.user, name=outfit_name)
        ids_1 = User_Cloths.objects.filter(pk__in = ids).values_list("cloths_id",flat=True)
        for item_id in ids_1:
            outfit.clothes.add(ClosetClothes.objects.get(clothes_id=item_id))
        outfit.save()

@login_required
def store_location(request):
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        user_profile = get_object_or_404(Profile, user=request.user)
        user_profile.location = f"{latitude},{longitude}"
        user_profile.save()
        return redirect("home")
    else:
        return render(request, "get_location.html")

@login_required
def worn(request, outfit_name=None):
    if outfit_name:
        items_ids = request.session.get("suggested_items", [])
        suggested_items = User_Cloths.objects.filter(id__in = items_ids)
        with transaction.atomic():
            for item in suggested_items:
                item.worn_count += 1
                item.save()
            adding_outfits(request, items_ids, outfit_name)
    else:
        return HttpResponseBadRequest("Outfit name is required.")
    return redirect("home")

@login_required
def all_outfits(request):
    outfits = Outfit.objects.filter(user=request.user).order_by("-add_date")
    return render(request, "all_outfits.html", {"outfits": outfits})

@login_required
def outfit_detail(request, outfit_id):
    outfit = get_object_or_404(Outfit, outfit_id=outfit_id)
    clothes_ids = outfit.clothes.values_list("clothes_id", flat=True)
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
    images = ClosetClothes.objects.filter(clothes_id__in=clothes_ids).order_by(custom_order)
    return render(request, "display_outfit.html", {"images": images, "outfit": outfit})

def remove_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfit, user=request.user, outfit_id=outfit_id)
    outfit.user_id = None
    outfit.save()

    return redirect('all_outfits')



