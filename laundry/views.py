from django.shortcuts import render, redirect,get_object_or_404
from closet.models import ClosetClothes


def laundry(request):
    clothes = ClosetClothes.objects.filter(user=request.user,worn_count__gt= 3)
    return render(request, 'laundry.html',{"clothes": clothes})

def reset(request,item_id):
    item = get_object_or_404(ClosetClothes, pk=item_id, user=request.user)
    item.worn_count = 0
    item.save()
    return redirect("laundry")