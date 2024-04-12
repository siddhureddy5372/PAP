from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClosetClothes, User_Cloths
from .forms import ImageUploadForm,AIDetectionForm
from .capsule_closet import ImageHandler
from closet.models import User_Cloths
from closet.global_defs import ClosetImageManager,ManageParameters
from .setup_cache import Caching
from django.http import JsonResponse
from django.contrib import messages
import json
from datetime import datetime


def use_existing(request):
    """
    View for adding an existing item to the user's closet.

    If a POST request is received, it adds the item to the user's closet
    and updates the image cache.

    Args:
        request: HTTP request object.

    Returns:
        JSON response indicating success or error.
    """
    if request.method == "POST":
        # Store all the data of json into an variable
        json_data = json.loads(request.body)
        
        # Extract the image URL from the JSON data
        image = json_data.get("image")
        images = ClosetImageManager(request)
        # Get the existing cloth object 
        cloth = get_object_or_404(ClosetClothes, image = image)
        # Create an new user cloth with the existing cloth
        User_Cloths.objects.create(user=request.user, cloths=cloth)
        # Update the cache of cloths
        images.get_images(update=True)
        messages.info(request, "Success! Image uploaded.")
    else:
        # Handle invalid request methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def find_match(request):
    '''
    View to check an find existing cloth.

    Args:
        request: HTTP request object.

    Returns:
        response_data: An json data with two keys-
                        hasMatch: Boolean.
                        Existing_image : image uyrl of existing cloth.
    '''

    if request.method == 'POST':
        # Extract parameters from the request
        brand = request.POST.get('brand')
        color = request.POST.get('color')
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory')

        # Filter cloth from db
        existing_cloth = ClosetClothes.objects.filter(
            brand=brand, color=color, category=category, subcategory=subcategory
        ).first()

        if existing_cloth is not None:
            # Construct the full URL of the matching image
            matching_image_url = existing_cloth.image.name
            response_data = {
                'hasMatch': True,
                'matchingImageUrl': matching_image_url
            }
        else:
            response_data = {
                'hasMatch': False,
                'matchingImageUrl': None
            }

        return JsonResponse(response_data)
    else:
        # Handle invalid request methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def remove_clothing(request,cloth_id):
    try:
        # Check if the user has the specified clothing item
        manage = ManageParameters(request)
        images = ClosetImageManager(request)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Use change_par with parameter want to change
        manage.change_par(User_Cloths, cloth_id,is_active = 0,deleted_date = current_time)
        images.get_images(update=True)
    # if there is no object in database
    except User_Cloths.DoesNotExist:
        pass
    return redirect('cloths')


@login_required
def upload(request):
    """
    View for handling image uploads by users.

    If a POST request is received, it processes the uploading cloth and updates the image cache.

    Args:
        request: HTTP request object.

    Returns:
        Redirects to the upload page after processing.
    """
    if request.method == "POST":
        images = ClosetImageManager(request)
        form = ImageUploadForm(request.user, request.POST, request.FILES)
        if ImageHandler.handle_image_upload_without_ai(request, form):
            images.get_images(update=True)
            return redirect("upload")
    else:
        form = ImageUploadForm(request.user)

    return render(request, "upload.html", {"form": form})

@login_required
def ai_upload(request):
    """
    View for handling AI-based image uploads by users.

    If a POST request is received, it processes the uploaded image
    using AI detection and updates the image cache.

    Args:
        request: HTTP request object.

    Returns:
        Redirects to the AI upload page after processing.
    """
    if request.method == "POST":
        form = AIDetectionForm(request.user,request.POST, request.FILES)
        if ImageHandler.handle_image_upload_with_ai(request, form):
            return redirect("ai")
    else:
        form = AIDetectionForm(request.user)
    return render(request, "ai_upload.html", {"form": form})

@login_required
def cloths(request):
    """
    View for displaying the user's closet.

    Returns:
        Renders the cloths.html template with user's images.
    """
    images = ClosetImageManager(request)
    distinct_user_images = images.get_images()
    return render(request, "cloths.html", {"user_images": distinct_user_images})

@login_required
def restore(request):
    """
    View for displaying the user's restoreable items.

    Returns:
        Renders the restore_clothes.html template with restoreable items.
    """
    images_restore = ClosetImageManager(request)
    distinct_user_images = images_restore.images_restore()
    return render(request,"restore_clothes.html",{"clothes":distinct_user_images})

def restoring(request,item_id):
    """
    View for restoring a previously removed item.

    Args:
        request: HTTP request object.
        item_id: ID of the item to be restored.

    Returns:
        Redirects to the restore page after restoration.
    """
    try:
        # Check if the user has the specified clothing item
        manage = ManageParameters(request)
        images = ClosetImageManager(request)
        manage.change_par(User_Cloths, item_id,is_active = 1,deleted_date = None)
        images.get_images(update=True)
    except User_Cloths.DoesNotExist:
        pass
    return redirect("restore")

def cloths_detail(request, item_id):
    """
    View for displaying details of a specific item.

    Args:
        request: HTTP request object.
        item_id: ID of the item to display details for.

    Returns:
        Renders the cloth_detail.html template with item details.
    """
    manage = Caching(request)
    data = manage.get_cloth(item_id)
    return render(request, "cloth_detail.html", {"item": data,"id":item_id})