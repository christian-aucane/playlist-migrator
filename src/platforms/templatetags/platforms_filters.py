from django import template

from platforms.models import OAuthToken


register = template.Library()


@register.filter
def is_connected_to_platform(user, platform):
    """
    Custom filter to check if the user is connected to the platform.
    """
    if user.is_authenticated:
        return OAuthToken.is_user_connected_to_platform(user, platform)
    return False
