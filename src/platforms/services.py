from .clients import get_client_for_platform
from .models import OAuthToken, PlatformServiceLog


class NoAccessTokenError(Exception):
    pass


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
    def __init__(self, user, platform):
        self.user = user
        self.platform = platform
        try:
            self.client = get_client_for_platform(platform=platform)
            token = OAuthToken.objects.get(user=user, platform=platform)
            self.client.authenticate_with_token_data(token_data=token.get_data_as_dict())
        except OAuthToken.DoesNotExist:
            raise NoAccessTokenError(f"User does not have an access token for {platform}.")

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

    def search_tracks(self, query):
        """
        Searches for tracks using the user's access token and logs the action in the database.

        Args:
            query (str): The search query.

        Returns:
            A list of tracks.
        """
        tracks = self.client.search_tracks(query=query)
        self._log_action(action="search", metadata={"count": len(tracks)})
        return tracks
