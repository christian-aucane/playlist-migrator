from django import template

from ..models import OAuthToken


register = template.Library()


@register.filter
def is_connected_to_platform(user, platform):
    """
    Custom filter to check if the user is connected to the platform.
    """
    if user.is_authenticated:
        return OAuthToken.is_user_connected_to_platform(user, platform)
    return False

@register.filter
def get_user_platforms(user):
    """
    Custom filter to get the platforms where the user is connected
    """
    if user.is_authenticated:
        return OAuthToken.get_user_platforms(user)
    return []
