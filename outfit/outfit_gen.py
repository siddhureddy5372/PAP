import os
import random
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from closet.models import ClosetClothes, User_Cloths
from user.models import Profile

def choose_random_item(items):
    """
    Choose a random item from the given queryset.
    """
    return random.choice(items) if items else None

def get_location(request):
    """
    Retrieve user's latitude and longitude from their profile location.
    """
    user_profile = Profile.objects.get(user=request.user)
    location = user_profile.location.split(",")
    return location[0], location[1]

def get_temperature(latitude, longitude):
    """
    Retrieve weather data from an external API based on latitude and longitude.
    """
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        data = response.json()
        temperature = data["main"]["temp"]
        return temperature
    except requests.RequestException as e:
        return None

@login_required
def suggest_outfit(request):
    """
    Suggest an outfit based on user's location and weather conditions.
    """
    latitude, longitude = get_location(request)
    temperature = get_temperature(latitude, longitude)

    # Retrieve user's clothing items
    user_clothes = User_Cloths.objects.filter(user=request.user).values_list('cloths_id', flat=True)
    clothes = ClosetClothes.objects.filter(clothes_id__in = user_clothes)

    # Filter clothing items based on weather conditions and user preferences
    suggested_items = []
    for category in ['jacket', 'hoodie', 't-shirt', 'joggers', 'jeans', 'boots', 'trainers']:
        items = clothes.filter(subcategory=category, worn_count__lte=3)
        if items.exists():
            suggested_items.append(choose_random_item(items))

    # Save suggested items to session for later use
    request.session["suggested_items"] = [item.clothes_id for item in suggested_items if item]

    return render(request, "home.html", {"outfit": suggested_items})
