import os
import base64
from django.utils.text import slugify
from datetime import datetime
from .models import User_Cloths
from django.contrib import messages
from PIL import Image
from io import BytesIO
from ximilar.client import FashionTaggingClient
import re

class ImageHandler:

    def __init__(self,request):
        self.request = request


    @staticmethod
    def handle_image_upload_without_ai(request, form):
        if form.is_valid():
            image_file = request.FILES["image"]
            output = ImageHandler.resize_image(image_file)
            current_datetime = datetime.now()

            # Extract information to generate image name based on that info
            brand = form.cleaned_data.get("brand")
            color = form.cleaned_data.get("color")
            category = form.cleaned_data.get("category")

            # Call function to generate a image name inside the same class
            image_name = ImageHandler.generate_image_name(brand, color, category)
            instance = form.save(commit=False)
            instance.add_date = current_datetime
            instance.image.save(f"{image_name}.png", output)
            instance.save()
            User_Cloths.objects.create(user=request.user, cloths=instance)

            messages.info(request, "Success! Image uploaded.")
            return True
        return False
    @staticmethod
    def correctify(category,subcategory):
        words = []
        sub = subcategory
        if "/" in subcategory:
            sub = subcategory.split("/")[-1]
        for part in category.split("/"):
                words.extend(re.findall(r'[A-Z][a-z]*', part))
        category_mappings = {
            "tops": "top",
            "jackets": "top",
            "coats": "top",
            "coat": "top",
            "blouses": "top",
            "cardigans": "top",
            "crop": "top",
            "shirts": "top",
            "hoodies": "top",
            "knitted": "top",
            "polo-shirts": "top",
            "shell": "top",
            "sweaters": "top",
            "sweatshirts": "top",
            "upper": "top",
            "t-shirts": "top",
            "tank": "top",
            "transparent": "top",
            "tunics": "top",
            "vests": "top",
            "wrap": "top",
            "pants": "bottom",
            "cargo": "bottom",
            "leggings": "bottom",
            "shorts": "bottom",
            "trousers": "bottom",
            "culottes": "bottom",
            "jeans": "bottom",
            "hotpants": "bottom",
            "sweatpants": "bottom",
            "boots": "shoes",
            "footwear": "shoes",
            "trainers": "shoes",
            "sneakers": "shoes"
        }
        for word in words: 
            if word.lower() in category_mappings:
                return category_mappings[word.lower()],sub
        else:
            return category_mappings[category.lower()],sub

    @staticmethod
    def handle_image_upload_with_ai(request, form):
        if form.is_valid():
            brand = form.cleaned_data.get("brand")
            image_file = request.FILES["image"]
            output = ImageHandler.resize_image(image_file)
            current_datetime = datetime.now()

            image_data = [{"_base64": base64.b64encode(output.getvalue()).decode("utf-8")}]  # Use the output of resize_image
            category, subcategory, color = ImageHandler.get_info(image_data)

            image_name = ImageHandler.generate_image_name(brand, color, category)

            

        
            instance = form.save(commit=False)
            instance.color = color
            instance.category = category
            instance.subcategory = subcategory
            instance.add_date = current_datetime
            instance.image.save(f"{image_name}.png", output)
            instance.save()
            User_Cloths.objects.create(user=request.user, cloths=instance)
            messages.info(request, "Success! Image uploaded with AI.")
            return True
        return False



    @staticmethod
    def generate_image_name(brand, color, category):
        brand_slug = slugify(brand)
        color_slug = color[:3]
        category_slug = category[:3]
        image_name = f"{brand_slug}_{color_slug}_{category_slug}"
        return image_name


    @staticmethod
    def resize_image(image_file):
        image = Image.open(image_file)
        resized_image = image.resize((720, 1080))
        output = BytesIO()
        resized_image.save(output, format="PNG")
        output.seek(0)
        return output

    @staticmethod
    def get_info(image_data):
        api_token = os.environ.get("XIMILAR_API_TOKEN")  # Your Ximilar API token
        fashion_client = FashionTaggingClient(token=api_token)
        result = fashion_client.detect_tags(image_data)
        category, subcategory, color = ImageHandler.parse_tags(result)
        category_r,subcategory = ImageHandler.correctify(category,subcategory)
        return category_r, subcategory, color

    @staticmethod
    def parse_tags(data):
        color = data["records"][0]["_objects"][0]["_tags"]["Color"][0]["name"]
        category = data["records"][0]["_objects"][0]["_tags"]["Category"][0]["name"]
        try:
            subcategory = data["records"][0]["_objects"][0]["_tags"]["Subcategory"][0]["name"]
        except KeyError:
            subcategory = category
        return category, subcategory, color
