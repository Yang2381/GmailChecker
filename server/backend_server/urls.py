from django.contrib import admin
from django.urls import path, re_path, include
from .views import login, create_user, create_pair, index, get_events
urlpatterns = [
    path('index', index),
    path('login', login),
    path('create_user', create_user),
    path('create_pair', create_pair),
    path('get_events', get_events)
]
