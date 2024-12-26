from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Track(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    duration_ms = models.PositiveIntegerField(help_text="The duration of the track in milliseconds.",
                                              null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def is_avaiable_on_platform(self, platform):
        """
        Check if the track is available on the given platform.
        """
        return TrackPlatformInfo.objects.filter(track=self, platform=platform).exists()


class TrackPlatformInfo(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="platform_infos")

    platform = models.CharField(max_length=255,
                                choices=[(platform, platform) for platform in settings.AVAILABLE_PLATFORMS])
    platform_id = models.CharField(max_length=255)
    url = models.URLField(help_text="The URL of the track on the platform.",
                          blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO : ajouter image (url ou fichier ?)

    class Meta:
        unique_together = ("track", "platform")
        ordering = ["platform"]
        verbose_name = "Track Platform Info"
        verbose_name_plural = "Track Platform Infos"

    def __str__(self):
        return f"{self.platform}: {self.track} ({self.platform_id})"


class UserTrack(models.Model):
    """
    Model for tracking user tracks.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    from_platform = models.CharField(max_length=255,
                                     choices=[(platform, platform) for platform in settings.AVAILABLE_PLATFORMS])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "track", "from_platform")
        ordering = ["-created_at"]
        verbose_name = "User Track"
        verbose_name_plural = "User Tracks"

    def __str__(self):
        return f"{self.user}: {self.track} ({self.from_platform})"

    def get_delete_url(self):
        return reverse("main_app:user_track_delete", kwargs={"pk": self.pk})
