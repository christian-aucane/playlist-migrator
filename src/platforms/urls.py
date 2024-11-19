from django.urls import path

from .views import OAuthRedirectView, OAuthCallbackView, DisconnectPlatformView

app_name = "platforms"

urlpatterns = [
    path("auth/<str:platform>/", OAuthRedirectView.as_view(), name="auth_redirect"),
    path("auth_callback/<str:platform>/", OAuthCallbackView.as_view(), name="auth_callback"),
    path("disconnect/<str:platform>/", DisconnectPlatformView.as_view(), name="disconnect"),
]
