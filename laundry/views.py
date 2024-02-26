from django.shortcuts import render, redirect,get_object_or_404
from closet.models import ClosetClothes,User_Cloths
from closet.global_defs import ClosetImageManager,ManageParameters

def laundry(request):
    images = ClosetImageManager(request)
    distinct_user_images = images.images(user_cloths__worn_count__gt=3)
    return render(request, 'laundry.html', {"list": distinct_user_images})


def reset(request, item_id):
    mangae = ManageParameters(request)
    mangae.change_par(User_Cloths, item_id,worn_count = 0)
    return redirect('laundry')