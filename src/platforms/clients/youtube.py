import json

from django.conf import settings
from django.utils import timezone

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .abstract import AbstractParser, AbstractClient


class YoutubeParser(AbstractParser):
    """
    Parser for the YouTube API
    """

    def parse_saved_tracks(self, data):
        """
        Parse the data returned by the API

        Parameters:
        data: The raw data returned by the API

        Returns: A list of track dicts
            {
                "title": track_title, (str)
                "artist": artist_names, (str)
                "album": album_name, (str)
                "duration_ms": duration_ms, (int)
                "platform_id": track_id, (str)
                "url": track_url, (str)
            }
        """
        parsed_data = []

        # TODO : améliorer le parsing des tracks ( vérifier si c'est de la musique, extraire l'artiste du titre ....)

        for item in data:
            track = item["snippet"]
            parsed_data.append(
                {
                    "title": track["title"],
                    "artist": track["channelTitle"],  # TODO : extraire l'artiste du titre ?
                    "album": None,  # TODO : ajouter l'album dans les données de l'API ?
                    "duration_ms": 0,  # TODO : ajouter la durée dans les données de l'API
                    "platform_id": item["id"],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                }
            )

        return parsed_data


class YoutubeClient(AbstractClient):
    """
    Client for the YouTube API
    """

    parser_class = YoutubeParser

    def __init__(self, client_secrets_file, scopes, redirect_uri=None):
        super().__init__()
        self.flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file,
            scopes,
            redirect_uri=redirect_uri
        )

    def get_auth_url(self):
        """
        Returns the authorization URL for the client.
        """
        return self.flow.authorization_url()[0]

    def authenticate_with_code(self, code):
        """
        Authenticates the client using an authorization code and stores the token data.

        Parameters:
        - code: The authorization code received from the callback.
        """
        # Exchange the code for credentials
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials

        self.token_data = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'expires_at': timezone.make_aware(credentials.expiry) if credentials.expiry else None,  # datetime aware (with timezone
            # information)
            'scope': " ".join(credentials.scopes) if credentials.scopes else None,
        }

        # Instantiate the YouTube service client
        self.client = build("youtube", "v3", credentials=credentials)

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

        credentials = Credentials(
            token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token"
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())  # Import Request from google.auth.transport.requests

        self.token_data = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": timezone.make_aware(credentials.expiry) if credentials.expiry else None,
            "scope": credentials.scopes if credentials.scopes else None,
        }

        # Instantiate the YouTube service client
        self.client = build("youtube", "v3", credentials=credentials)

    def fetch_saved_tracks(self):
        """
        Use self.client to get the list of saved tracks

        Returns: Raw data of the saved tracks
        """
        request = self.client.videos().list(
            part="snippet",
            myRating="like"
        )

        tracks = []
        while request is not None:
            response = request.execute()
            tracks.extend(response["items"])
            request = self.client.videos().list_next(request, response)
        return tracks
