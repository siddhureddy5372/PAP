import os
import random
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from closet.models import User_Cloths
from user.models import Profile
#from closet.setup_cache import Caching
from .ai_model import get_outfit_recommendation_images

def choose_random_item(items):
    """
    Choose a random item from the given queryset.
    """
    return random.choice(items) if items else None


def updating_items(request,new_items):
    request.session["suggested_items"] = new_items # Creates an key "suggested_items" = new_items if not an empty [].

def get_location(request):
    """
    Retrieve user's latitude and longitude from their profile location.
    """
    cache_key = f"{request.user.id}_location"
    cache_data = cache.get(cache_key)
    if cache_data:
        print("FROM CACHE")
        location = cache_data.split(",")
        return location[0],location[1]
    else:
        print("FROM DB")
        user_profile = Profile.objects.get(user=request.user)
        cache.set(cache_key,user_profile.location,timeout=2000)
        location = user_profile.location.split(",")
        return location[0], location[1]

def get_weather_data(request):
    """
    Retrieve weather data from an external API based on latitude and longitude.
    """
    cache_key = f"weather_data"
    if cache.get(cache_key):
        cache_data = cache.get(cache_key)
        return cache_data["temperature"],cache_data["weather_condition"]
    else:
        try:
            profile = request.user.profile
            if profile.location:
                latitude, longitude = get_location(request)   
            else:
                # Set default weather data if location is not available
                return 20,"Cloudy0"
        except ObjectDoesNotExist:
            # User does not have a profile
            # Set default weather data
            return 20,"Cloudy7"
        
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()
            weather_data = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "weather_condition": data["weather"][0]["main"]
            }
            cache.set(cache_key,weather_data,timeout= 2000)
            return weather_data["temperature"],weather_data["weather_condition"]
        except requests.RequestException as e:
            return 20,"Cloudy77"


def select_cloths(data, **kwargs):
    items_1 = []
    for key, value in kwargs.items():
        if isinstance(value, list):
            for val in value:
                filtered_data = data.filter(**{key: val})
                items_1.append(choose_random_item(filtered_data))
        else:
            filtered_data = data.filter(**{key: value})
            items_1.append(choose_random_item(filtered_data))
    return items_1




@login_required
def suggest_outfit(request):
    """
    Suggest an outfit based on user's location, weather conditions.
    """
    # Build cache key to store latest outfit generated cloth id's
    cache_key = f"{request.user.id}_outfit"
    cache_key_1 = f"{request.user.id}_clothes"
    suggested_items_data = None
    # Save suggested items to session for later use
    session = []
    if (random.randint(0,2) != 0) and cache.get(cache_key_1):
        suggested_items_data,session = get_outfit_recommendation_images(request)
        change = True

    
    if not suggested_items_data:
        change = False
        temperature,weather_condition = get_weather_data(request)

        # Retrieve user's clothing items
        user_clothes = User_Cloths.objects.filter(user=request.user, worn_count__lt=4,is_active = True)

        # Define weather-based outfit suggestions
        suggested_items = []
        print(type(temperature))
        # Adjust outfit suggestions based on weather conditions
        if weather_condition in ['Rain', 'Drizzle', 'Thunderstorm', "Clouds"]:
            # Suggest waterproof jacket, boots, and umbrella for rainy weather
            suggested_items.append(select_cloths(user_clothes,cloths__subcategory=["coat",'t-shirt',"jeans","boots"]))       
            
        elif weather_condition == 'Snow':
            # Suggest insulated jacket, snow boots, and gloves for snowy weather
            suggested_items.append(select_cloths(user_clothes,cloths__subcategory =['winter jacket', 'hoodies', 'jeans', 'boots']))
        elif 10 <= temperature <= 25:
            # Suggest light clothing for hot weather
            suggested_items.append(select_cloths(user_clothes,cloths__subcategory = ['t-shirt', 'joggers', 'sneakers']))
        elif temperature < 10:
            print("jf")
            # Suggest warm clothing for cold weather
            suggested_items.append(select_cloths(user_clothes,cloths__subcategory = ['jacket', 'hoodies', 'jeans', 'sneakers']))
        else:
            suggested_items.append(select_cloths(user_clothes,cloths__subcategory=["t-shirt","shorts","sneakers"]))

        suggested_items_data = []
        for item in suggested_items[0]:
            if item:
                suggested_items_data.append((item.id, item.cloths.image))
                session.append(item.id)
        cache.delete(cache_key)
        cache.set(cache_key,session,timeout=200)
    else:
        cache.delete(cache_key)
        cache.set(cache_key,session,timeout=200)
        weather_condition = "Clouds"
    return render(request, "home.html", {"outfit": suggested_items_data, "con": weather_condition,"change": change})
