
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('opportunity/', views.opportunity_crud.as_view()),
    path('team/',views.team_crud.as_view()),
    path('team/managing/',views.team_managing.as_view()),
    path('team/inviter/',views.InviterTeamInvites.as_view()),
    path('team/receiver/',views.ReceiverTeamInvites.as_view()),
    path('search/student',views.SearchStudent.as_view()),
]