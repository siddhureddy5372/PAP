from django.urls import path
from . import views,outfit_gen
from closet.views import cloths_detail

urlpatterns = [
    path("home/", outfit_gen.suggest_outfit, name="home" ),
    path("worn/<str:outfit_name>/",views.worn, name="worn"),
    path("location/",views.store_location,name = "location"),
    path("all_outfits/",views.all_outfits, name="all_outfits"),
    path('display_outfit/<int:outfit_id>/', views.outfit_detail, name='display_outfit'),
    path('remove_outfit/<int:outfit_id>/', views.remove_outfit, name='remove_outfit'),
    path("testing/",views.test,name="testing")
]