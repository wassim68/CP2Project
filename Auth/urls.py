from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
urlpatterns = [
    path('Login',views.Login.as_view()),
    path('Signup',views.Signup.as_view()),
    path('Refresh',TokenRefreshView.as_view()),
    path('user',views.acc.as_view()),
    path('otpemail',views.ForgotPass.as_view()),
    path('user/<int:id>/',views.getuser.as_view()),
    path('userpassword',views.reset_password.as_view()),
    path('post/<int:id>/',views.savedpost.as_view()),
    path('post',views.post.as_view()),
    path('Fcm',views.Fcm.as_view()),
    path('google',views.GoogleAuthenticate.as_view()),
    path('linkdein',views.LinkedInAuthenticate.as_view()),
    path('notfi',views.notfication.as_view()),
]
