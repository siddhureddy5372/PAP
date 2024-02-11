from django.urls import path
from . import views,outfit_gen
from closet.views import cloths_detail

urlpatterns = [
    path("home", outfit_gen.suggest_outfit, name="home" ),
    path("worn",views.increment, name="worn"),
    path("location",views.store_location,name = "location"),
    path("all_outfits",views.all_outfits, name="all_outfits"),
    path('display_outfit/<int:outfit_id>/', views.outfit_detail, name='display_outfit'),
]