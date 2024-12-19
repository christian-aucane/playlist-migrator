from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.conf import settings

User = get_user_model()


class OAuthToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="oauth_tokens",
        help_text="The user who owns this token."
    )
    platform = models.CharField(
        choices=[(platform, platform) for platform in settings.AVAILABLE_PLATFORMS],
        max_length=50,
        help_text="The platform the token belongs to (e.g., 'youtube', 'spotify')."
    )
    access_token = models.TextField(
        help_text="The access token provided by the platform."
    )
    refresh_token = models.TextField(
        blank=True,
        null=True,
        help_text="The refresh token provided by the platform."
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The expiration time of the access token."
    )
    scope = models.TextField(
        blank=True,
        null=True,
        help_text="The scopes associated with the token."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "platform")
        ordering = ["platform"]
        verbose_name = "OAuth Token"
        verbose_name_plural = "OAuth Tokens"

    def is_expired(self):
        """Check if the access token has expired."""
        return self.expires_at and now() >= self.expires_at

    def get_data_as_dict(self):
        """
        Returns the token data as a dictionary.
        """
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "scope": self.scope
        }

    def __str__(self):
        return f"{self.user.username} - {self.platform}"

    @classmethod
    def is_user_connected_to_platform(cls, user, platform):
        if not user.is_authenticated:
            raise ValueError("User is not authenticated.")
        obj = cls.objects.filter(user=user, platform=platform).first()
        if not user.is_authenticated or not obj or obj.is_expired():
            return False

        return True


class PlatformServiceLog(models.Model):
    """Model for tracking user platform actions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=255,
                                choices=[(platform, platform) for platform in settings.AVAILABLE_PLATFORMS])
    action = models.CharField(max_length=255)  # TODO : Ajouter les actions possibles dans choices
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Platform Service Log"
        verbose_name_plural = "Platform Service Logs"

    def __str__(self):
        return f"{self.user}: {self.platform} ({self.action})"
