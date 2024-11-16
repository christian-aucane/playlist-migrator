from django.urls import path

from .views import CustomLoginView, CustomLogoutView, SignupView


app_name = "authenticate"

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path("signup/", SignupView.as_view(), name="signup")
]
