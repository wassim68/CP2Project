
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('opportunity/', views.opportunity_crud.as_view()),
    path('team/',views.team_crud.as_view()),
    path('team/managing/',views.team_managing.as_view()),
    path('team/inviter/',views.InviterTeamInvites.as_view()),
    path('team/receiver/',views.ReceiverTeamInvites.as_view()),
    path('user/search',views.SearchUser.as_view()),
    path('saved/search',views.Search_saved.as_view()),
    path('opportunity/explorer',views.get_opportunities.as_view()),
    path('student/dashboard',views.dashboard.as_view()),
    path('team/<int:id>',views.team_by_id.as_view()),
    path('opportunity/<int:id>',views.opp_by_id.as_view()),

]