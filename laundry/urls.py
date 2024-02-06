from django.urls import path
from . import views

urlpatterns = [
    path("laundry",views.laundry,name="laundry"),
    path('reset/<int:item_id>/', views.reset, name='reset'),

]