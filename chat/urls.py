from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.RoomName.as_view()),
    path('messages', views.Messages.as_view()),

]