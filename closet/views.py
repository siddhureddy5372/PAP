from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ClosetClothes, User_Cloths
from .forms import ImageUploadForm,AIDetectionForm
from .capsule_closet import ImageHandler
from closet.global_defs import ClosetImageManager
from closet.models import User_Cloths
from closet.global_defs import ClosetImageManager,ManageParameters
from .setup_cache import Caching



def remove_clothing(request,cloth_id):
    try:
        # Check if the user has the specified clothing item
        manage = ManageParameters(request)
        manage.change_par(User_Cloths, cloth_id,is_active = 0)
    except User_Cloths.DoesNotExist:
        pass
    return redirect('cloths')



@login_required
def upload(request):
    if request.method == "POST":
        images = ClosetImageManager(request)
        form = ImageUploadForm(request.user, request.POST, request.FILES)
        if ImageHandler.handle_image_upload(request, form):
            images.get_images(update=True)
            return redirect("upload")
    else:
        form = ImageUploadForm(request.user)

    return render(request, "upload.html", {"form": form})



@login_required
def test(request):
    if request.method == "POST":
        form = AIDetectionForm(request.user,request.POST, request.FILES)
        if ImageHandler.handle_image_upload(request,form,True):
            return redirect("test")
    else:
        form = AIDetectionForm(request.user)
    return render(request, "test.html", {"form": form})


@login_required
def cloths(request):
    images = ClosetImageManager(request)
    distinct_user_images = images.images()
    return render(request, "cloths.html", {"user_images": distinct_user_images})


@login_required
def restore(request):
    images_restore = ClosetImageManager(request)
    distinct_user_images = images_restore.images_restore()
    return render(request,"restore_clothes.html",{"clothes":distinct_user_images})

def restoring(request,item_id):
    try:
        # Check if the user has the specified clothing item
        manage = ManageParameters(request)
        manage.change_par(User_Cloths, item_id,is_active = 1)
    except User_Cloths.DoesNotExist:
        pass
    return redirect("restore")

def cloths_detail(request, item_id):
    manage = Caching(request)
    data = manage.get_cloth(item_id)
    return render(request, "cloth_detail.html", {"item": data})

