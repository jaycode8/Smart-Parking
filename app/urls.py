from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('slots', views.slots),
    path('slot/<slug:id>', views.slot),
    path('parking', views.parking),
    path('parking/<slug:id>', views.parked_car),
    path('users', views.users),
    path('signin', views.signin),
    path('user/<slug:userId>', views.user),
    path('logout', views.logOut),
    path('detection', views.detect_plate)
]