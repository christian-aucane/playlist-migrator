from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from .clients import get_client_for_platform
from .models import OAuthToken


# ==============================================================================
# BASE CLASSES
# ==============================================================================
class BasePlatformView(LoginRequiredMixin, View):
    @staticmethod
    def get_client(platform):
        """Retrieves the client associated with the given platform."""
        return get_client_for_platform(platform)


# ==============================================================================
# Auth views
# ==============================================================================
class OAuthRedirectView(BasePlatformView):
    def get(self, request, platform):
        """
        Redirects the user to the platform authentication page.
        """
        client = self.get_client(platform)
        return HttpResponseRedirect(client.get_auth_url())


class OAuthCallbackView(BasePlatformView):
    def get(self, request, platform):
        """
        Handles the callback from the platform authentication page.
        """
        client = self.get_client(platform)
        # TODO : ajouter try except si la connexion echoue
        client.authenticate_with_code(request.GET["code"])

        token_data = client.token_data

        # Store the token data in the database
        OAuthToken.objects.update_or_create(
            user=request.user,
            platform=platform,
            defaults={
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": token_data.get("expires_at"),
                "scope": token_data.get("scope"),
            }
        )

        return HttpResponseRedirect(reverse("main_app:index"))


class DisconnectPlatformView(BasePlatformView):
    def get(self, request, platform):
        """
        Disconnects the user from the given platform.
        """
        filters = {"user": request.user}

        if platform != "all":
            filters["platform"] = platform

        tokens = OAuthToken.objects.filter(**filters)

        if tokens is None:
            messages.error(request, "No account to disconnect")
        else:
            tokens.delete()
            messages.success(request, "Disconnected successfully")

        return HttpResponseRedirect(reverse("main_app:index"))
