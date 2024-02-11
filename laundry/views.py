from django.shortcuts import render, redirect,get_object_or_404
from closet.models import ClosetClothes,User_Cloths


def laundry(request):
    items = User_Cloths.objects.filter(user=request.user).values_list('cloths_id', flat=True)
    clothes = ClosetClothes.objects.filter(clothes_id__in = items,worn_count__gte= 3)
    return render(request, 'laundry.html',{"clothes": clothes})

def reset(request,item_id):
    item = get_object_or_404(ClosetClothes, pk=item_id)
    item.worn_count = 0
    item.save()
    return redirect("laundry")