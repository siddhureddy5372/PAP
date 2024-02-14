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


def updating_items(request,new_items):
    request.session["suggested_items"] = new_items # Creates an key "suggested_items" = new_items if not an empty [].

def get_location(request):
    """
    Retrieve user's latitude and longitude from their profile location.
    """
    user_profile = Profile.objects.get(user=request.user)
    location = user_profile.location.split(",")
    return location[0], location[1]

def get_weather_data(latitude, longitude):
    """
    Retrieve weather data from an external API based on latitude and longitude.
    """
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
        return weather_data
    except requests.RequestException as e:
        return None

@login_required
def suggest_outfit(request):
    """
    Suggest an outfit based on user's location, weather conditions, and user preferences.
    """
    latitude, longitude = get_location(request)
    weather_data = get_weather_data(latitude, longitude)

    if weather_data:
        temperature = weather_data["temperature"]
        humidity = weather_data["humidity"]
        wind_speed = weather_data["wind_speed"]
        weather_condition = weather_data["weather_condition"]

        # Retrieve user's clothing items
        user_clothes = User_Cloths.objects.filter(user=request.user, worn_count__lt=4,is_active = True)

        # Define weather-based outfit suggestions
        suggested_items = []

        # Adjust outfit suggestions based on weather conditions
        if weather_condition in ['Rain', 'Drizzle', 'Thunderstorm', "Clouds"]:
            # Suggest waterproof jacket, boots, and umbrella for rainy weather
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='jacket', cloths__waterproof=True)))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='jeans')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='boots', cloths__waterproof=True)))
        elif weather_condition == 'Snow':
            # Suggest insulated jacket, snow boots, and gloves for snowy weather
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='jacket')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='boots')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='gloves')))
        elif temperature > 25:
            # Suggest light clothing for hot weather
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='t-shirt')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='joggers')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='sneakers')))
        elif temperature < 10:
            # Suggest warm clothing for cold weather
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='jacket')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='hoodies')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='jeans')))
            suggested_items.append(choose_random_item(user_clothes.filter(cloths__subcategory='sneakers')))

        # Save suggested items to session for later use
        session = []
        suggested_items_data = []
        for item in suggested_items:
            if item:
                suggested_items_data.append((item.id, item.cloths.image))
                session.append(item.id)
        updating_items(request,session)
    else:
        suggested_items_data = []

    return render(request, "home.html", {"outfit": suggested_items_data, "con": session})
