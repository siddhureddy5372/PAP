from django.shortcuts import render, redirect
from closet.models import User_Cloths
from closet.global_defs import ClosetImageManager,ManageParameters

def laundry(request):
    images = ClosetImageManager(request)
    # This returns the cloths needed to wash with id's and images
    distinct_user_images = images.get_images(update = False, laundry = True,
                                              user_cloths__worn_count__gt=3 )
    return render(request, 'laundry.html', {"list": distinct_user_images})


def reset(request, item_id):
    mangae = ManageParameters(request)
    # Changes item_id's worn_count parameter to 0 
    mangae.change_par(User_Cloths, item_id,worn_count = 0)
    images = ClosetImageManager(request)
    images.get_images(update = True)
    return redirect('laundry')