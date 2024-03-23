from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from closet.models import User_Cloths
from user.models import Profile
from .models import Outfit,OutfitClothes
from django.db import transaction
from django.http import HttpResponseBadRequest
from closet.global_defs import ClosetImageManager
from .ai_model import get_outfit_recommendation_images
from django.core.cache import cache
from closet.setup_cache import Caching



def test(request):
    clothes = get_outfit_recommendation_images(request)
    return render(request, "testing.html",{"images":clothes})

def adding_outfits(request, ids, outfit_name):
    if len(ids) >0:
        images = ClosetImageManager(request)
        outfit = Outfit.objects.create(user=request.user, name=outfit_name)
        for item_id in ids:
            outfit.clothes.add(item_id)
        outfit.save()
        images.get_images(update=True)

@login_required
def store_location(request):
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        user_profile = get_object_or_404(Profile, user=request.user)
        user_profile.location = f"{latitude},{longitude}"
        user_profile.save()
        manage = Caching(request)
        manage.get_profile("update")
        return redirect("profile")
    else:
        return redirect("profile")

@login_required
def worn(request,outfit_name=None):
    if outfit_name:
        #items_ids = request.session.get("suggested_items", [])
        cache_key = f"{request.user.id}_outfit"
        cache_data = cache.get(cache_key)
        if cache_data:
            items_ids = cache_data
            int_list = [int(x) for x in items_ids]
            suggested_items = User_Cloths.objects.filter(id__in = int_list)
            with transaction.atomic():
                for item in suggested_items:
                    item.worn_count += 1
                    item.save()
                adding_outfits(request, int_list, outfit_name)
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
    clothes_ids = list(OutfitClothes.objects.filter(outfit_id=outfit_id).values_list("clothes_id", flat=True))
    images = ClosetImageManager(request)
    print(clothes_ids)
    distinct_user_images = images.get_images_outfit(clothes_ids)
    
    return render(request, "display_outfit.html", {"images": distinct_user_images, "outfit": outfit})

def remove_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfit, user=request.user, outfit_id=outfit_id)
    outfit.user_id = None
    outfit.save()

    return redirect('all_outfits')



