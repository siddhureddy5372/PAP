from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClosetClothes, User_Cloths
from .forms import ImageUploadForm
from django.contrib import messages
from PIL import Image
from io import BytesIO
from django.utils.text import slugify
from datetime import datetime
from DressRight.global_defs import images,images_restore
from django.http import HttpResponse

def find_matching_cloth(brand, color, category, subcategory):
    existing_cloth = ClosetClothes.objects.filter(
        brand=brand, color=color, category=category, subcategory=subcategory
    ).first()
    if existing_cloth:
        return existing_cloth.clothes_id,existing_cloth.image.name
    else:
        return None,None


def remove_clothing(request,cloth_id):
    clothing_id = cloth_id
    try:
        # Check if the user has the specified clothing item
        user_clothing = User_Cloths.objects.get(pk = clothing_id)
        # Delete the association between the user and the clothing item
        user_clothing.is_active = False
        user_clothing.save()
    except User_Cloths.DoesNotExist:
        pass
    return redirect('cloths')


def generate_image_name(brand, color, category):
    # Convert brand name to lowercase and replace spaces with underscores
    brand_slug = slugify(brand)

    # Create slugs for color and category
    color_slug = color[:3]
    category_slug = category[:3]

    # Concatenate slugs with underscores
    image_name = f"{brand_slug}_{color_slug}_{category_slug}"

    return image_name


@login_required
def upload(request):
    if request.method == "POST":
        form = ImageUploadForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded image
            image_file = request.FILES["image"]

            # Open the image using Pillow
            image = Image.open(image_file)

            # Resize the image to 720x1080 pixels
            resized_image = image.resize((720, 1080))

            current_datetime = datetime.now()
            # Convert the resized image to BytesIO object
            output = BytesIO()
            resized_image.save(output, format="PNG")
            output.seek(0)  # Reset the BytesIO pointer to the beginning

            brand = form.cleaned_data.get("brand")
            color = form.cleaned_data.get("color")
            category = form.cleaned_data.get("category")
            subcategory = form.cleaned_data.get("subcategory")

            # Set image name based on brand, color, and category
            image_name = generate_image_name(brand, color, category)

            # Check if there is a matching cloth
            id_of_item, existing_image_path = find_matching_cloth(
                brand, color, category, subcategory
            )

            if existing_image_path:
                User_Cloths.objects.create(user=request.user, cloths_id=id_of_item)
            else:
                # If no matching cloth is found, save the new cloth with the generated image name
                instance = form.save(commit=False)
                instance.add_date = current_datetime
                instance.image.save(f"{image_name}.png", output)  # Save image with PNG extension
                instance.save()
                User_Cloths.objects.create(user=request.user, cloths=instance)

            messages.info(request, "Success! Image uploaded.")
            return redirect("upload")
    else:
        form = ImageUploadForm(request.user)

    return render(request, "upload.html", {"form": form})


@login_required
def cloths(request):
    distinct_user_images = images(request)
    return render(request, "cloths.html", {"user_images": distinct_user_images})


@login_required
def restore(request):
    distinct_user_images = images_restore(request)
    return render(request,"restore_clothes.html",{"clothes":distinct_user_images})

def restoring(request,item_id):
    item = get_object_or_404(User_Cloths,user = request.user,pk = item_id)
    item.is_active = True
    item.save()
    return redirect("restore")

def cloths_detail(request, item_id):
    item = get_object_or_404(ClosetClothes, user_cloths__pk=item_id)
    cloth = get_object_or_404(User_Cloths,pk = item_id)
    return render(request, "cloth_detail.html", {"item": item,"cloth" : cloth})
