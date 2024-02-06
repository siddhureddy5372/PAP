from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import logout
from closet.models import ClosetClothes
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,ProfileForm
from .models import Profile


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username is not None and password is not None:
            user = auth.authenticate(username=username, password=password)

            if user:
                auth.login(request, user)
                if hasattr(request.user, 'profile'):
                    return redirect("home")
                else:
                    return redirect("create_profile")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Username and password are required.")
    
    return render(request, "login.html")

@login_required
def create_profile(request):
    if request.method == "POST":
        user = request.user
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            redirect("home")
    else:
        profile_form = ProfileForm()

    # Render the template with the form
    return render(request, 'create_profile.html', {'profile': profile_form}) 

def edit_profile(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=user_profile)
    
    context = {'form': form}
    return render(request, 'edit_profile.html', context)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})
    
@login_required
def logout(request):
    auth.logout(request)
    return redirect("/")  



@login_required
def profile(request):
    user_id = request.user.id
    user_profile = Profile.objects.get(user=user_id)
    return render(request,"profile.html",{"user" : user_profile})