from django.urls import path
from . import views

urlpatterns = [
    path("",views.login,name="login"),
    path("register",views.register, name="register"),
    path("logout", views.logout, name= "logout"),
    path('profile', views.profile, name='profile'),
    path("create_profile",views.create_profile,name = "create_profile"),
    path("edit_profile", views.edit_profile,name="edit_profile"),
]