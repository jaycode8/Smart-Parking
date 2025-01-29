from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('slots', views.slots),
    path('users', views.users),
    path('signin', views.signin),
]