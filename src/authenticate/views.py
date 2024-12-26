from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic import TemplateView, CreateView

from authenticate.forms import CustomUserCreationForm

User = get_user_model()


class CustomLoginView(LoginView):
    template_name = "authenticate/login.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class SignupView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "authenticate/signup.html"
    success_url = reverse_lazy("authenticate:login")
