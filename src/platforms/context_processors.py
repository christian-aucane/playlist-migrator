from django.conf import settings


def available_platforms(request):
    return {"available_platforms": settings.AVAILABLE_PLATFORMS}
