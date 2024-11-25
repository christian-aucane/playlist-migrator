from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.contrib.sites.shortcuts import get_current_site

from platforms.models import OAuthToken


class BasePlatformView(View):
    def get_redirect_uri(self, platform):
        """Returns the absolute URL of the redirection after authentication."""
        relative_url = reverse("platforms:auth_callback", args=[platform])
        domain = get_current_site(self.request).domain
        return f"http://{domain}{relative_url}"

    def get_client(self, platform):
        """Retrieves the client associated with the given platform."""
        platform_config = settings.PLATFORMS_CLIENTS.get(platform)

        if platform_config:
            client_class_path = platform_config["client_class"]
            client_kwargs = platform_config["client_kwargs"]
            client_class = self._import_client_class(client_class_path)
            client_kwargs["redirect_uri"] = self.get_redirect_uri(platform)
            return client_class(**client_kwargs)

        # Raise an error if the platform is not configured
        raise ValueError(f"Unknown platform: {platform}")

    def _import_client_class(self, path):
        """Import dynamically the client class from its path."""
        from importlib import import_module
        module_path, class_name = path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, class_name)


class OAuthRedirectView(BasePlatformView):
    def get(self, request, platform):
        """
        Redirects the user to the platform authentication page.
        """
        client = self.get_client(platform)
        # TODO : ajouter try except et retourner une page d'erreur
        return HttpResponseRedirect(client.get_auth_url())


class OAuthCallbackView(BasePlatformView):
    def get(self, request, platform):
        """
        Handles the callback from the platform authentication page.
        """
        client = self.get_client(platform)
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

        return HttpResponseRedirect(reverse("home"))


class DisconnectPlatformView(LoginRequiredMixin, View):
    def get(self, request, platform):
        """
        Disconnects the user from the given platform.
        """
        OAuthToken.objects.filter(user=request.user, platform=platform).delete()

        # TODO : ajouter un message de confirmation
        # Redirect to the home page
        return HttpResponseRedirect(reverse("home"))