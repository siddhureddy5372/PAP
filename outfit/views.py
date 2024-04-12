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
from django.contrib import messages

def adding_outfit(request, ids, outfit_name):
    if len(ids) >= 2:
        outfit = Outfit.objects.create(user=request.user, name=outfit_name)
        for item_id in ids:
            outfit.clothes.add(item_id)
        outfit.save()

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

def worn_count(ids):
    # Convert those id's into integer
    int_list = [int(x) for x in ids]
    
    # Get objects query with int_list items objects
    suggested_items = User_Cloths.objects.filter(id__in = int_list)
    with transaction.atomic():
        for item in suggested_items:
            # This add's 1 to each item which has been worn 
            item.worn_count += 1
            # Save that object
            item.save()
    return int_list

@login_required
def worn(request,outfit_name=None):
    # get an name for outfit
    if outfit_name:
        cache_key = f"{request.user.id}_outfit"
        # Retreive latest generated outfit cloth_id's.
        cache_data = cache.get(cache_key)
        if cache_data:
            items_ids = cache_data
            # A def handling increment of worncount
            int_list = worn_count(items_ids)
            images = ClosetImageManager(request)
            # This will update cache of clothes 
            images.get_images(update=True)
            # A function which adds this outfit into history
            adding_outfit(request, int_list, outfit_name)
    else:
        return HttpResponseBadRequest("Outfit name is required.")
    return redirect("home")

def check (ids,data):
    int_list = [int(x) for x in ids]
    for i in data:
        if i["id"] in int_list and i["worn_count"] > 3:
            return False
        else:
            continue
    return True

@login_required
def worn_agian(request,ids):
    int_ids = str(ids).strip("[]").split(",")
    cache_key = f"{request.user.id}_clothes"
    cached_data = cache.get(cache_key)
    if check(int_ids,cached_data):
        worn_count(int_ids)
        global_def = ClosetImageManager(request)
        global_def.get_images(update=True)
    else:
        messages.info(request, "All cloths are not avalible.")
    return redirect("all_outfits")

@login_required
def all_outfits(request):
    outfits = Outfit.objects.filter(user=request.user).order_by("-add_date")
    return render(request, "all_outfits.html", {"outfits": outfits})

@login_required
def outfit_detail(request, outfit_id):
    outfit = get_object_or_404(Outfit, outfit_id=outfit_id)
    clothes_ids = list(OutfitClothes.objects.filter(outfit_id=outfit_id).values_list("clothes_id", flat=True))
    images = ClosetImageManager(request)
    ids = str(clothes_ids)
    distinct_user_images = images.get_images_outfit(clothes_ids)
    return render(request, "display_outfit.html", {"images": distinct_user_images, "outfit": outfit,"ids" : ids})

def remove_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfit, user=request.user, outfit_id=outfit_id)
    outfit.user_id = None
    outfit.save()

    return redirect('all_outfits')



