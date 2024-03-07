from django.shortcuts import render,redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm,ProfileForm
from .models import Profile
from django.core.cache import cache
from closet.setup_cache import Caching

@ csrf_protect
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

@ csrf_protect
@login_required
def create_profile(request):
    if request.method == "POST":
        user = request.user
        profile_form = ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect("home")
    else:
        profile_form = ProfileForm()

    # Render the template with the form
    return render(request, 'create_profile.html', {'profile': profile_form}) 

@login_required
def edit_profile(request):
    manage = Caching(request)
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Set the user field
            profile.save()
            manage.get_profile("update")
            return redirect("profile")
    else:
        form = ProfileForm(instance=user_profile)
    
    context = {'form': form,"user":user_profile}
    return render(request, 'edit_profile.html', context)


@ csrf_protect
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
    manage = Caching(request)
    user_profile = manage.get_profile("get")
    return render(request,"profile.html",{"user" : user_profile})