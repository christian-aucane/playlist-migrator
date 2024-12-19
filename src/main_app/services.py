from django.conf import settings
from django.db import transaction

from .models import Track, TrackPlatformInfo, UserTrack
from platforms.services import PlatformService


class MainAppService:
    """
    Main App Service.

    Args:
        user (User): The user.
    """

    def __init__(self, user):
        self.user = user

    @staticmethod
    def search_track(title, artist):
        """
        Searches for a track based on the title and artist.

        Args:
            title (str): The title of the track.
            artist (str): The artist of the track.

        Returns:
            track (Track): The retrieved track.
        """
        # TODO : améliorer la recherche ?
        track = Track.objects.filter(title=title, artist=artist).first()
        return track

    def get_or_create_track(self, title, artist, album=None, duration_ms=None):
        """
        Searches for an existing track based on the title and artist.
        If it doesn't exist, a new track is created with the provided information.

        Args:
            title (str): The title of the track.
            artist (str): The artist of the track.
            album (str, optional): The album of the track. Defaults to None.
            duration_ms (int, optional): The duration of the track in milliseconds. Defaults to None.

        Returns:
            track (Track): The retrieved or created track.
            created (bool): A flag indicating whether the track was created (True) or retrieved (False).
        """
        track = self.search_track(title, artist)

        if track:
            if album and track.album != album:
                track.album = album
            if duration_ms and track.duration_ms != duration_ms:
                track.duration_ms = duration_ms

            track.save()
            created = False

        else:
            track = Track.objects.create(
                title=title,
                artist=artist,
                album=album,
                duration_ms=duration_ms
            )
            created = True

        return track, created

    def _search_and_create_on_other_platforms(self, track, platform=None):
        """
        Search for tracks on other platforms and create them if they don't exist.

        Args:
            track (Track): The track to search and create on other platforms.
        """
        print(f"Searching and creating on other platforms, for {track} ({platform})")
        other_platforms = list(settings.AVAILABLE_PLATFORMS)
        print(f"Other platforms: {other_platforms}")
        print(f"Platform: {platform}")

        if platform is not None:
            other_platforms.remove(platform)

        for platform_name in other_platforms:

            # TODO : mettre a jour les infos si la ligne existe ??
            if TrackPlatformInfo.objects.filter(track=track, platform=platform_name).exists():
                print(f"Track already exists on {platform_name}")
                continue

            print(f"Searching and creating on {platform_name}")

            try:
                platform_service = PlatformService(user=self.user, platform=platform_name)
            except PlatformService.NoAccessTokenError:
                continue

            track_data = platform_service.search_track(track.title, track.artist)

            if track_data:
                print(f"Found on {platform_name}")
                if track_data.get("album") is not None and track.album is None:
                    track.album = track_data["album"]

                if track_data.get("duration_ms") is not None and track.duration_ms is None:
                    track.duration_ms = track_data["duration_ms"]

                track.save()
                TrackPlatformInfo.objects.create(track=track,
                                                 platform=platform_name,
                                                 platform_id=track_data["platform_id"],
                                                 url=track_data.get("url"))
            else:
                print(f"Not found on {platform_name}")

    @transaction.atomic
    def add_user_track(self, from_platform, track_data):
        """
        Add a user track to the database.

        Args:
            from_platform (str): The platform the track was saved from.
            track_data (dict): The track data.
                {
                    "title": track_title, (str)
                    "artist": artist_names, (str)
                    "album": album_name, (str)
                    "duration_ms": duration_ms, (int)
                    "platform_id": track_id, (str)
                    "url": track_url, (str)
                }

        Returns:
            The created or retrieved user track object and a boolean indicating whether it was created or retrieved.
        """
        track, track_created = self.get_or_create_track(
            title=track_data["title"],
            artist=track_data["artist"],
            album=track_data.get("album"),
            duration_ms=track_data.get("duration_ms")
        )

        platform_info, _ = TrackPlatformInfo.objects.get_or_create(
            track=track,
            platform=from_platform,
            defaults={
                "platform_id": track_data["platform_id"],
                "url": track_data["url"],
            }
        )

        if track_created:
            self._search_and_create_on_other_platforms(track, platform=from_platform)

        user_track, created = UserTrack.objects.get_or_create(
            user=self.user,
            track=track,
            from_platform=from_platform
        )

        return user_track, created

    @transaction.atomic
    def update_user_tracks(self, platform):
        """
        Update the user tracks for the given platform without deleting all records.

        Args:
            platform (str): The platform to update the user tracks for.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        platform_service = PlatformService(platform=platform, user=self.user)
        saved_tracks = platform_service.fetch_saved_tracks()

        if not saved_tracks:
            return False

        # Get all currently saved tracks for this user and platform
        current_user_tracks = UserTrack.objects.filter(user=self.user, from_platform=platform)
        current_platform_ids = set(
            TrackPlatformInfo.objects.filter(track__in=current_user_tracks.values("track"), platform=platform)
            .values_list("platform_id", flat=True)
        )

        # Extract track IDs from the API response
        fetched_platform_ids = set(track["platform_id"] for track in saved_tracks)

        # Identify new tracks to add
        new_tracks = [track for track in saved_tracks if track["platform_id"] not in current_platform_ids]

        # Identify tracks to remove
        tracks_to_remove = current_user_tracks.filter(
            track__platform_infos__platform_id__in=current_platform_ids - fetched_platform_ids
        )

        print("New tracks: ", len(new_tracks))
        print("Tracks to remove: ", len(tracks_to_remove))

        # Add new tracks
        for track_data in new_tracks:
            self.add_user_track(from_platform=platform, track_data=track_data)

        # Remove tracks no longer liked
        tracks_to_remove.delete()

        return True
