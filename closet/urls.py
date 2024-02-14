from django.urls import path
from . import views

urlpatterns = [
    path("upload", views.upload, name="upload" ),
    path("cloths", views.cloths, name="cloths"),
    path("restore",views.restore, name="restore"),
    path('cloths/<int:item_id>/', views.cloths_detail, name='cloths_detail'),
    path('remove/<int:cloth_id>/', views.remove_clothing, name='remove_clothing'),
    path("restore/<int:item_id>/",views.restoring, name="restoring")
]