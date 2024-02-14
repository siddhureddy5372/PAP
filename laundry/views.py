from django.shortcuts import render, redirect,get_object_or_404
from closet.models import ClosetClothes,User_Cloths
from DressRight.global_defs import images

def laundry(request):
    distinct_user_images = images(request,user_cloths__worn_count__gt=3)
    return render(request, 'laundry.html', {"list": distinct_user_images})


def reset(request, item_id):
    item = get_object_or_404(User_Cloths, pk=item_id)
    item.worn_count = 0
    item.save()
    return redirect('laundry')