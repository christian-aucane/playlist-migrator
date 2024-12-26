import re
from pprint import pprint

from django.conf import settings
from django.utils import timezone

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import isodate

from .abstract import AbstractParser, AbstractClient


class YoutubeParser(AbstractParser):
    """
    Parser for the YouTube API
    """

    @staticmethod
    def parse_track(data):
        """
        Parse the data returned by the API

        Parameters:
        data: The raw data returned by the API

        Returns: A track dict
            {
                "title": track_title, (str)
                "artist": artist_names, (str)
                "album": album_name, (str)
                "duration_ms": duration_ms, (int)
                "platform_id": track_id, (str)
                "url": track_url, (str)
            }
        """
        snippet = data["snippet"]
        # TODO : ajouter d'autres catégories ?
        category_id = snippet.get("categoryId")
        if category_id is not None and category_id != "10":
            return None


        content_details = data.get("contentDetails")

        if content_details is None:
            duration_ms = 0
            platform_id = data["id"]["videoId"]
        else:
            duration_ms = YoutubeParser._parse_duration_ms(content_details["duration"])
            platform_id = data["id"]

        track_title = snippet["title"]
        channel_title = snippet["channelTitle"]
        title, artist = YoutubeParser._extract_title_and_artist(track_title, channel_title)
        return {
            "title": title,
            "artist": artist,
            "album": None,
            "duration_ms": duration_ms,
            "platform_id": platform_id,
            "url": f"https://www.youtube.com/watch?v={platform_id}",
        }

    @staticmethod
    def _parse_duration_ms(duration):
        """
        Parse the duration string into milliseconds

        Parameters:
        duration: The duration string

        Returns: The duration in milliseconds
        """
        duration = isodate.parse_duration(duration)
        return duration.total_seconds() * 1000


    @staticmethod
    def _extract_title_and_artist(title, channel_title):
        """
        Extract the title and artist from the track title and channel title

        Parameters:
        title: The track title
        channel_title: The channel title

        Returns: The title and artist
        """
        # TODO : améliorer l'extraction au fur et a mesure, comment ??

        title = title
        artist = channel_title

        # TODO : ajouter les feat dans artist

        parts = title.split("-")
        if len(parts) >= 2:
            artist = parts[0].strip()
            title = "-".join(parts[1:]).strip()
        title = re.sub(r"\(.*?\)", "", title)
        title = re.sub(r'\[[^\]]*\]', '', title)

        return title, artist


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

    def set_unauthenticated_client(self):
        """
        Set self.client without user authentication
        """
        self.client = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    def fetch_saved_tracks(self):
        """
        Use self.client to get the list of saved tracks

        Returns: Raw data of the saved tracks
        """
        request = self.client.videos().list(
            part="snippet,contentDetails",
            myRating="like"
        )

        tracks = []
        while request is not None:
            response = request.execute()
            tracks.extend(response["items"])
            request = self.client.videos().list_next(request, response)
        return tracks

    def fetch_search(self, query, limit=10):
        """
        Use self.client to search a track

        Returns: Raw data of the search
        """

        request = self.client.search().list(
            part="snippet",

            q=query,
            maxResults=limit
        )

        data = request.execute()

        return data["items"]

    def like_track(self, track_id):
        """
        Use self.client to like a track
        """
        request = self.client.videos().rate(id=track_id, rating="like")
        request.execute()

        return True

    def unlike_track(self, track_id):
        """
        Use self.client to unlike a track
        """
        request = self.client.videos().rate(id=track_id, rating="none")
        request.execute()

        return True

    def clear_saved_tracks(self):
        """
        Use self.client to clear saved tracks
        """
        request = self.client.videos().deleteRating()
        request.execute()

        return True
