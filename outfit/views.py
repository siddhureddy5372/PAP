from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from closet.models import ClosetClothes
from django.db import transaction
from .models import Outfit
import random

def choose_random_item(category_queryset):
    if category_queryset.exists():
        eligible_items = category_queryset.filter(worn_count__lte=3)
        if eligible_items:
            return random.choice(eligible_items)  # Use eligible_items instead of category_queryset
    return None


def updating_items(request,new_items):
    request.session["suggested_items"] = new_items # Creates an key "suggested_items" = new_items if not an empty [].

def adding_outfits(request,ids):
    if len(ids) != 0:
        outfit = Outfit.objects.create(user_id=request.user.id, name='Default name')
        for item in ids:
            outfit.clothes.add(ClosetClothes.objects.get(clothes_id = item))
        outfit.save()


@login_required
def increment(request):
    items_ids = request.session.get('suggested_items', []) # gets value of key "suggested_items" if not an return empty [].
    suggested_items = ClosetClothes.objects.filter(user=request.user,clothes_id__in = items_ids)
    with transaction.atomic():
        for item in suggested_items:
            if item is not None:
                item.worn_count += 1
                item.save()
        adding_outfits(request,items_ids)

    return redirect("home")


@login_required
def suggest_outfit(request):
    weather_data = {"temperature": 0, "humidity": 80, "wind_speed": 10, "rain_chance": "heavy"}

    suggested_items = []
    id_of_items = []
    if weather_data["temperature"] < 10:
        suggested_items.extend([
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['jacket', 'hoodie'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['t-shirt'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['joggers', 'jeans'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['boots', 'trainers']))
        ])
    elif 10 <= weather_data["temperature"] < 20:
        suggested_items.extend([
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['jacket', 'hoodie', 'coat'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['t-shirt'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['joggers', 'jeans'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['boots', 'trainers', 'sneakers']))
        ])
    elif 20 <= weather_data["temperature"] < 30:
        suggested_items.extend([
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['t-shirt', 'shirt', 'hoodie'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['jeans', 'shorts', 'pants'])),
            choose_random_item(ClosetClothes.objects.filter(user=request.user, subcategory__in=['trainers', 'sneakers']))
        ])
    user_id = request.user.id
    for item in suggested_items:
        if item is not None :
            id_of_items.append(item.clothes_id)
    updating_items(request,id_of_items)
    suggest = request.session.get('suggested_items', []) # gets value of key "suggested_items" if not an return empty [].
    return render(request, 'home.html', {"outfit":suggested_items, "user": user_id,"ids":id_of_items,"suggest":suggest})
