from django.conf import settings
from django.db import transaction

from ..models import Track, TrackPlatformInfo, UserTrack


@transaction.atomic
def save_user_track(user, track_data, platform):
    """
    Registers a song and its associations for a given user.

    Args:
        user: User instance.
        track_data: Dictionary containing track information.
        platform: Platform name (e.g. 'spotify', 'youtube').

    Returns:
        Tuple (UserTrack, created): The user/track association and a Boolean indicating whether it's a new entry.
    """
    if platform not in settings.AVAILABLE_PLATFORMS:
        raise ValueError(f"Invalid platform: {platform}")
    required_fields = ["title", "artist", "platform_id"]
    for field in required_fields:
        if field not in track_data:
            raise ValueError(f"Missing required field: {field}")

    track, _ = Track.objects.get_or_create(
        title=track_data["title"],
        artist=track_data["artist"],
        album=track_data.get("album"),
        defaults={"duration_ms": track_data.get("duration_ms")}
    )

    platform_info, _ = TrackPlatformInfo.objects.get_or_create(
        track=track,
        platform=platform,
        defaults={
            "platform_id": track_data["platform_id"],
            "url": track_data.get("url"),
        }
    )

    user_track, created = UserTrack.objects.get_or_create(
        user=user,
        track=track,
        from_platform=platform
    )

    return user_track, created
