from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import TemplateView


class CustomLoginView(LoginView):
    template_name = "authenticate/login.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class SignupView(TemplateView):
    template_name = "core/home"  # TODO : modifier
