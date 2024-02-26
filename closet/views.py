from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClosetClothes, User_Cloths
from .forms import ImageUploadForm,AIDetectionForm
from .capsule_closet import ImageHandler
from closet.global_defs import ClosetImageManager




def remove_clothing(request,cloth_id):
    clothing_id = cloth_id
    try:
        # Check if the user has the specified clothing item
        user_clothing = User_Cloths.objects.get(pk = clothing_id,user_id = request.user.id)
        # Delete the association between the user and the clothing item
        user_clothing.is_active = False
        user_clothing.save()
    except User_Cloths.DoesNotExist:
        pass
    return redirect('cloths')



@login_required
def upload(request):
    if request.method == "POST":
        form = ImageUploadForm(request.user, request.POST, request.FILES)
        if ImageHandler.handle_image_upload(request, form):
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
    item = get_object_or_404(User_Cloths,user = request.user,pk = item_id)
    item.is_active = True
    item.save()
    return redirect("restore")

def cloths_detail(request, item_id):
    item = get_object_or_404(ClosetClothes, user_cloths__pk=item_id)
    cloth = get_object_or_404(User_Cloths,pk = item_id)
    return render(request, "cloth_detail.html", {"item": item,"cloth" : cloth})

