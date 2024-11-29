from importlib import import_module

from django.conf import settings
from django.urls import reverse


def _get_current_site():
    """Retrieve the current site from the Sites framework."""
    return


def _import_client_class(path):
    """Import dynamically the client class from its path."""
    module_path, class_name = path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)


def _get_redirect_uri(platform):
    """Returns the absolute URL of the redirection after authentication."""
    relative_url = reverse("platforms:auth_callback", args=[platform])
    domain = settings.DEFAULT_DOMAIN
    protocol = settings.DEFAULT_PROTOCOL
    # TODO : ajouter le protocole dynamiquement (http ou https)
    return f"{protocol}://{domain}{relative_url}"


def get_client_for_platform(platform):
    """Retrieves the client associated with the given platform."""

    platform_config = settings.PLATFORMS_CLIENTS.get(platform)

    if platform_config:
        client_class_path = platform_config["client_class"]
        client_kwargs = platform_config["client_kwargs"]
        client_class = _import_client_class(client_class_path)


        client_kwargs["redirect_uri"] = _get_redirect_uri(platform)
        return client_class(**client_kwargs)

    # Raise an error if the platform is not configured
    raise ValueError(f"Unknown platform: {platform}")
