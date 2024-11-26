from django.utils import timezone

from spotipy import SpotifyOAuth, Spotify

from .abstract import AbstractParser, AbstractClient


class SpotifyParser(AbstractParser):
    """
    Parser for the Spotify API
    """

    def parse_saved_tracks(self, data):
        """
        Parse the data returned by the API

        Parameters:
        data: The raw data returned by the API

        Returns: A list of tracks dicts
        """
        parsed_data = []

        for item in data["items"]:
            track = item["track"]
            parsed_data.append(
                {
                    "title": track["name"],
                    "artist": ", ".join([artist["name"] for artist in track["artists"]]),
                    "album": track["album"]["name"],
                    "duration_ms": track["duration_ms"],
                    "platform_id": track["id"],
                    "url": track["external_urls"]["spotify"],
                }
            )
        return parsed_data


class SpotifyClient(AbstractClient):
    """
    Client for the Spotify API

    Attributes:
        client_id: The client id
        client_secret: The client secret
        redirect_uri: The redirect uri
        scopes: The scopes
    """
    parser_class = SpotifyParser

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
        Set the token data in self.token_data
        Set the client in self.client

        Parameters:
        - code: The authorization code received from the callback.
        """
        # TODO : instancier client spotify
        token = self.auth_manager.get_access_token(code)
        self.token_data = {
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
            "expires_at": timezone.make_aware(timezone.datetime.fromtimestamp(token["expires_at"])),  # datetime aware (with timezone  # information)
            "scope": token["scope"],
        }

        self.client = Spotify(auth=self.token_data["access_token"])

    def authenticate_with_token_data(self, token_data):
        """
        Authenticates the client using a token and stores the token data
        - If the token is expired it will be refreshed
        - If the token is invalid it will raise an error

        - Set the token data in self.token_data
        - Set the client in self.client

        Parameters
        token_data: A dictionary with the access token and other information
           {"access_token": "your_access_token",
            "refresh_token": "your_refresh_token",
            "expires_at": "expires_at_datetime_aware",
            "scope": "your_scope"}
        """
        if token_data["expires_at"] > timezone.now():
            token = self.auth_manager.refresh_access_token(refresh_token=token_data["refresh_token"])

            self.token_data = {
                "access_token": token["access_token"],
                "refresh_token": token["refresh_token"],
                "expires_at": timezone.make_aware(timezone.datetime.fromtimestamp(token["expires_at"])),
                # datetime aware (with timezone  # information)
                "scope": token["scope"],
            }

        else:
            self.token_data = token_data

        self.client = Spotify(auth=self.token_data["access_token"])

    def fetch_saved_tracks(self):
        """
        Use self.client to get the list of saved tracks

        Returns: Raw data of the saved tracks
        """
        return self.client.current_user_saved_tracks()

