from django.urls import path
from . import views

urlpatterns = [
    path("upload", views.upload, name="upload" ),
    path("cloths", views.cloths, name="cloths"),
    path('cloths/<int:item_id>/', views.cloths_detail, name='cloths_detail'),
]