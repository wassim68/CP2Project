from django.urls import path
from . import views
urlpatterns = [
    path('application/<int:id>/',views.applications.as_view()),
    path('application',views.application_crud.as_view()),
    path('applications/<int:id>/',views.deleteapplication.as_view()),
    path('<int:id>/',views.company_app_management.as_view()),
    path('<int:id>/accept',views.accept),
    path('<int:id>/reject',views.reject),
    path('choose/<int:id>/',views.choose_app.as_view()),
    path('search/',views.search.as_view()),
    path('search/applied',views.search_applied.as_view()),
    path('web/<int:id>/',views.webapp.as_view()),
    path('reject_applicant/<int:id>/',views.rejectapplicant.as_view()),
]
