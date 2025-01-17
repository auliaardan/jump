from django.contrib.auth import views as auth_views
from django.urls import path

from accounts.views import SignUpView, CompleteProfileView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("complete-profile/", CompleteProfileView.as_view(), name="complete_profile"),
]
