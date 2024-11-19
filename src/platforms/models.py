from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()


class OAuthToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="oauth_tokens",
        help_text="The user who owns this token."
    )
    platform = models.CharField(
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