from .clients import get_client_for_platform
from .models import OAuthToken, PlatformServiceLog


class PlatformService:
    """
    Platform service class.

    This class provides a common interface for platform services.

    Attributes:
        user: User instance.
        platform: Platform name (e.g. 'spotify', 'youtube').

    Raises:
        NoAccessTokenError: If the user does not have an access token for the platform.
        ValueError: If an error occurs while initializing the client.
    """

    class NoAccessTokenError(Exception):
        """
        Exception raised when the user does not have an access token for the platform.
        """
        pass

    def __init__(self, user, platform):
        self.user = user
        self.platform = platform
        try:
            self.client = get_client_for_platform(platform=platform)
            token = OAuthToken.objects.get(user=user, platform=platform)
            self.client.authenticate_with_token_data(token_data=token.get_data_as_dict())
        except OAuthToken.DoesNotExist:
            raise PlatformService.NoAccessTokenError(f"User does not have an access token for {platform}.")

    def _log_action(self, action, metadata):
        """
        Logs an action in the database.

        Args:
            action (str): The action to log.
            metadata (dict): The metadata associated with the action.
        """
        PlatformServiceLog.objects.create(user=self.user, platform=self.platform, action=action, metadata=metadata)

    def fetch_saved_tracks(self):
        """
        Fetches the saved tracks for the user and logs the action in the database.

        Returns:
            A list of saved tracks.
        """
        saved_tracks = self.client.get_saved_tracks()
        self._log_action(action="fetch_saved_tracks", metadata={"count": len(saved_tracks)})
        return saved_tracks

    def search_track(self, title, artist):
        """
        Searches for tracks using the user's access token and logs the action in the database.

        Args:
            title (str): The title of the track to search for.
            artist (str): The artist of the track to search for.

        Returns:
            A list of tracks.
        """
        track = self.client.search_track(title=title, artist=artist)

        self._log_action(action="search_track", metadata={"query": {"title": title, "artist": artist},
                                                          "success": track is not None})

        return track

    def like_track(self, track_id):
        """
        Likes a track using the user's access token and logs the action in the database.

        Args:
            track_id (str): The ID of the track to like.

        Returns:
            bool: True if the track was liked successfully, False otherwise.
        """
        success = self.client.like_track(track_id=track_id)
        self._log_action(action="like_track", metadata={"track_id": track_id, "success": success})

        return success

    def unlike_track(self, track_id):
        """
        Unlikes a track using the user's access token and logs the action in the database.

        Args:
            track_id (str): The ID of the track to unlike.

        Returns:
            bool: True if the track was unliked successfully, False otherwise.
        """
        success = self.client.unlike_track(track_id=track_id)
        self._log_action(action="unlike_track", metadata={"track_id": track_id, "success": success})

        return success

    def clear_saved_tracks(self):
        """
        Clears the user's saved tracks using the user's access token and logs the action in the database.

        Returns:
            bool: True if the saved tracks were cleared successfully, False otherwise.
        """
        success = self.client.clear_saved_tracks()
        self._log_action(action="clear_saved_tracks", metadata={"success": success})

        return success
