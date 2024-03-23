from django.shortcuts import render, redirect
from closet.models import User_Cloths
from closet.global_defs import ClosetImageManager,ManageParameters

def laundry(request):
    ''' View for laundry managment for user clothes.

        Args:
            request: HTTP request object.

        Returns:
            Renders the laundry.html template with user's cloths which have worn more than 3 times with images.
    '''

    images = ClosetImageManager(request)
    # This returns the cloths needed to wash with id's and images
    distinct_user_images = images.get_images(update = False, laundry = True, user_cloths__worn_count__gt=3)
    return render(request, 'laundry.html', {"list": distinct_user_images})


def reset(request, item_id):
    ''' View to reset an cloth worn count to 0.

        Args:
            request: HTTP request object.
            item_id: id of the cloth that has been washed.

        Returns:
            Redirects to laundry after changing worn count.
    '''

    mangae = ManageParameters(request)
    # Changes item_id's worn_count parameter to 0 
    mangae.change_par(User_Cloths, item_id,worn_count = 0)
    images = ClosetImageManager(request)
    images.get_images(update = True)
    return redirect('laundry')