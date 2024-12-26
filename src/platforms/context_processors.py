from django.conf import settings


def available_platforms(request):
    """
    Context processor to get the available platforms in templates
    """
    return {"available_platforms": settings.AVAILABLE_PLATFORMS}
