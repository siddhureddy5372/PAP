from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ClosetClothes
from .forms import ImageUploadForm
from django.contrib import messages

@login_required
def upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request, "Success! Image uploaded.")
            return redirect('upload')
    else:
        form = ImageUploadForm(request.user)

    return render(request, 'upload.html', {'form': form})

@login_required
def cloths(request):
    user_images = ClosetClothes.objects.filter(user=request.user)
    return render(request,"cloths.html", {'user_images': user_images})

def cloths_detail(request, item_id):
    item = get_object_or_404(ClosetClothes, pk=item_id)
    return render(request, 'cloth_detail.html', {'item': item})