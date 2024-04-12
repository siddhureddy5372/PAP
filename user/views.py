import threading
from django.shortcuts import render,redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm,ProfileForm
from .models import Profile
from closet.setup_cache import UpdateCache
from closet.setup_cache import Caching
from django.core.exceptions import ObjectDoesNotExist

@ csrf_protect
def login(request):
    ''' View to login the user.

        Args:
            request: HTTP request object.

        Returns:
            Redirects to home or create profile after user info.
    '''

    if request.method == "POST":
        # Retrives the data from the POST
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username is not None and password is not None:
            # auth.authenticate returns True if the user exists else Flase
            user = auth.authenticate(username=username, password=password)
            if user:
                # Logs in the user
                auth.login(request, user)
                # Checks if the user already have a Profile created 
                if hasattr(request.user, 'profile'):
                    update = UpdateCache(request)
                    # Configure the Thread that stores all the data in cache
                    cache_thread = threading.Thread(target=update.setup())
                    # Start the cache
                    cache_thread.start()
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
    ''' This takes an form before saving it checks if it is valid if yes creats an profile in db.
        
        Args:
            request: HTTP request object.

        Returns:
            Redircts to the home after creating the profile
    '''

    if request.method == "POST":
        user = request.user
        profile_form = ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.location = "40.03555433333333,-8.820991666666666"
            profile.save()
            return redirect("home")
        else:
            print(profile_form.errors)
    else:
        profile_form = ProfileForm()

    # Render the template with the form
    return render(request, 'create_profile.html', {'profile': profile_form}) 

@login_required
def edit_profile(request):

    ''' Here the user can edit his profile, Caching is an class with different methods so that all the function i will be using to cache will be encapsulated in one class.

        Args:
            request: HTTP request object.

        Returns:
            Redirects to the profile after saving changes and updating the cache.
       '''

    try:
        user_profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        user_profile = None
    
    if request.method == 'POST':
        # Load the Caching class into an variable
        manage = Caching(request)
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Set the user field
            profile.location = "40.03555433333333,-8.820991666666666"
            profile.save()
            # After the changes update the cache of profile
            manage.get_profile("update")
            return redirect("profile")
    else:
        form = ProfileForm(instance=user_profile)
    
    context = {'form': form,"user":user_profile}
    return render(request, 'edit_profile.html', context)


@ csrf_protect
def register(request):

    ''' This is where the users get registered and i'm using forms of django it is like an blueprint on 
        how should the form should be like. After checking the form is valid or no save the data and redirct the user to 
        main url ("/"). 
        
        Args:
            request: HTTP request object.

        Returns:
            Redirects to main url after saving user.
        '''

    if request.method == "POST":
        # Store the form from HTML into an varible
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})
    
@login_required
def logout(request):
    # logs out the user
    auth.logout(request)
    return redirect("/")  



@login_required
def profile(request):
    manage = Caching(request)
    # Retreives the profile from cache
    user_profile = manage.get_profile("get")
    return render(request,"profile.html",{"user" : user_profile})