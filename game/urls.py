from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.main),
    path('rules/', views.rules),
    path('about/', views.about),
    path('new_game/', views.new_game),
    path('find_game/', views.find_game),
    path('lobby/<int:pk>/', views.lobby),
    path('new_game/lobby/', views.create_lobby),
    path('new_game/join_lobby/', views.join_lobby),
    #url(r'^lobby/$', views.lobby , name='lobby'),
    #path('new_game/<int:pk>/', views.create_lobby),
]