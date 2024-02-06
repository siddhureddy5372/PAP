from django.urls import path
from . import views
from closet.views import cloths_detail

urlpatterns = [
    path("home", views.suggest_outfit, name="home" ),
    path("worn",views.increment, name="worn"),
]