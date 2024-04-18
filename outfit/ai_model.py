import pandas as pd
from closet.models import ClosetClothes, User_Cloths
from django.core.cache import cache
import random
from closet.global_defs import ClosetImageManager

def get_outfit_recommendation_images(request):

    # Fetch user's clothes data
    cache_key = f"{request.user.id}_clothes"
    cache_data = cache.get(cache_key)
    if cache_data:
        clothing_data = pd.DataFrame(cache_data)
        _id = "id"

    # Define harmonious color combinations
    harmonious_combinations = [
        ("black", "dark blue", "dark blue", "green"),
        ("black", "black", "white", "grey"),
        ("cream","dark blue","black","blue"),
        ("navy", "white", "white", "grey"),
        ("brown", "white", "white", "khaki"),
        ("olive", "white", "white", "khaki"),
        ('Grey', 'White', 'Dark Blue', 'Black'),
        ('Yellow', 'Pink', 'Blue', 'Brown'),
        ('Black', 'White', 'Beige', 'Brown'),
        ('Grey', 'Green', 'Black', 'White'),
        ('Blue', 'Pink', 'Yellow', 'Beige'),
        ('Black', 'Grey', 'Dark Blue', 'Brown'),
        ('White', 'Green', 'Yellow', 'Pink'),
        ('Grey', 'Blue', 'Beige', 'White'),
        ('Black', 'Red', 'Grey', 'Dark Blue'),
        ('Yellow', 'Blue', 'Red', 'White'),
    ]
    random.shuffle(harmonious_combinations)

    # Create a DataFrame to store available items
    available_items_df = pd.DataFrame(columns=['top', 't-shirt', 'bottom', 'shoes'], index=range(len(harmonious_combinations)))


    # Iterate over each color combination
    for i, combination in enumerate(harmonious_combinations):

        # Initialize a flag to track if all colors in the combination are available
        all_colors_available = True
        combination_items = {}
        # Iterate over each category and color in the combination
        for category, color in zip(['top',"t-shirt",'bottom', 'shoes'], combination):
            if category == "t-shirt":
                filtered_items = clothing_data[(clothing_data['subcategory'] == category) & clothing_data['color'].str.contains(color, case=False, na=False)]
            else:
                filtered_items = clothing_data[(clothing_data['category'] == category) & clothing_data['color'].str.contains(color, case=False, na=False)]
            # Check if any items match the category and color
            if not filtered_items.empty:
                # Select a random item from the filtered items
                selected_item = filtered_items.sample(1).iloc[0]
                combination_items[category] = selected_item[_id]
            else:
                # Set the flag to False if no matching items are found
                all_colors_available = False
                break  # Exit the loop if any color is not available
           

        # If all colors in the combination are available, select those items
        if all_colors_available:
            available_items_df.loc[i] = combination_items
            break  # Exit the loop if a suitable combination is found


    # Fetch image URLs for the selected items
    extracted_data = []
    ids = []
    # if there was 
    if cache_data:
        objects = list(filter(lambda obj: obj["id"] in combination_items.values(), cache_data))
        extracted_data = [(item["id"], item["image"]) for item in objects]
        ids = list(combination_items.values())

    return extracted_data,ids
