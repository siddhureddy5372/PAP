from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClosetClothes, User_Cloths
from .forms import ImageUploadForm
from django.contrib import messages
from PIL import Image
from io import BytesIO
from datetime import datetime
from django.db.models import Case, When, IntegerField

def find_matching_cloth(brand, color, category, subcategory):
    existing_cloth = ClosetClothes.objects.filter(
        brand=brand, color=color, category=category, subcategory=subcategory
    ).first()
    if existing_cloth:
        return existing_cloth.clothes_id,existing_cloth.image.name
    else:
        return None,None


@login_required
def upload(request):
    if request.method == "POST":
        form = ImageUploadForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded image
            image_file = request.FILES["image"]

            # Open the image using Pillow
            image = Image.open(image_file)

            # Resize the image to 1080x1080 pixels
            resized_image = image.resize((720, 1080))

            current_datetime = datetime.now()
            # Convert the resized image to BytesIO object
            output = BytesIO()
            resized_image.save(output, format="JPEG")
            output.seek(0)  # Reset the BytesIO pointer to the beginning

            brand = form.cleaned_data.get("brand")
            color = form.cleaned_data.get("color")
            category = form.cleaned_data.get("category")
            subcategory = form.cleaned_data.get("subcategory")

            # Check if there is a matching cloth
            id_of_item,existing_image_path = find_matching_cloth(
                brand, color, category, subcategory
            )

            if existing_image_path:
                User_Cloths.objects.create(user=request.user, cloths_id=id_of_item)

            else:
                # If no matching cloth is found, save the new cloth with its own image
                instance = form.save(commit=False)
                instance.add_date = current_datetime
                instance.image.save(image_file.name, output)
                instance.save()
                User_Cloths.objects.create(user=request.user, cloths=instance)

            messages.info(request, "Success! Image uploaded.")
            return redirect("upload")
    else:
        form = ImageUploadForm(request.user)

    return render(request, "upload.html", {"form": form})


@login_required
def cloths(request):
    custom_order = Case(
        When(category='top', then=Case(
            When(subcategory='t-shirt', then=1),
            default=0
        )),
        When(category='bottom', then=1),
        When(category='shoes', then=2),
        default=3,  # For any other category not specified, set it to a higher value
        output_field=IntegerField()
    )
    user_images = ClosetClothes.objects.filter(user_cloths__user=request.user).order_by(custom_order)
    return render(request, "cloths.html", {"user_images": user_images})


def cloths_detail(request, item_id):
    item = get_object_or_404(ClosetClothes, pk=item_id)
    return render(request, "cloth_detail.html", {"item": item})
