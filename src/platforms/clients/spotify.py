from django.utils import timezone

from spotipy import SpotifyOAuth

from .base import BaseClient


class SpotifyClient(BaseClient):
    def __init__(self, client_id, client_secret, redirect_uri, scopes):
        super().__init__()
        self.auth_manager = SpotifyOAuth(client_id=client_id,
                                         client_secret=client_secret,
                                         redirect_uri=redirect_uri,
                                         scope=scopes)

    def get_auth_url(self):
        return self.auth_manager.get_authorize_url()

    def authenticate_with_code(self, code):
        """
        Authenticates the client using an authorization code and stores the token data.

        Parameters:
        - code: The authorization code received from the callback.
        """
        token = self.auth_manager.get_access_token(code)
        self.token_data = {
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
            "expires_at": timezone.make_aware(timezone.datetime.fromtimestamp(token["expires_at"])),  # datetime aware (with timezone  # information)
            "scope": token["scope"],
        }
