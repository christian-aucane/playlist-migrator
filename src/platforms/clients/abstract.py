import json
from abc import ABC, abstractmethod
from difflib import SequenceMatcher

from django.conf import settings


class AbstractParser(ABC):
    """
    Abstract class for all APIs parsers
    """

    @staticmethod
    @abstractmethod
    def parse_track(data):
        """
        Parse the data returned by the API

        Parameters:
        data: The raw data returned by the API

        Returns: A track dict or None
            {
                "title": track_title, (str)
                "artist": artist_names, (str)
                "album": album_name, (str)
                "duration_ms": duration_ms, (int)
                "platform_id": track_id, (str)
                "url": track_url, (str)
            }
        """
        pass

    def parse_tracks(self, data):
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

        for track in data:
            parsed_track = self.parse_track(track)
            if parsed_track is not None:
                parsed_data.append(parsed_track)
        return parsed_data


class AbstractClient(ABC):
    """
    Base class for all APIs clients
    """
    parser_class = None  # This must be set in subclasses

    def __init__(self):
        self._token_data = None
        self._client = None
        if self.parser_class is None or not issubclass(self.parser_class, AbstractParser):
            raise TypeError(
                f"{self.__class__.__name__} must define a parser_class that inherits from BaseParser."
            )
        self.parser = self.parser_class()

    def get_saved_tracks(self):
        """
        Returns the saved tracks for the authenticated user
        """
        data = self.fetch_saved_tracks()

        if settings.DEBUG:  # TODO : supprimer ce bout de code ??
            with open(settings.BASE_DIR.parent / "raw_data" / f"saved_tracks_{self.__class__.__name__}.json", "w") as f:
                json.dump(data, f, indent=4)

        return self.parser.parse_tracks(data)

    def search_track(self, title, artist):
        """
        Search for track using the authenticated user's access token
        """
        data = self.fetch_search(query=self.concat_query(title, artist), limit=1)
        try:
            if settings.DEBUG:  # TODO : supprimer ce bout de code ??
                with open(settings.BASE_DIR.parent / "raw_data" / f"search_track_{self.__class__.__name__}_{title}_{artist}.json",
                          "w") as f:
                    json.dump(data, f, indent=4)
        except OSError:
            pass

        if len(data) == 0:
            return None

        parsed_track = self.parser.parse_track(data[0])

        if self._check_search_similarity(parsed_track, title, artist):
            return parsed_track

        return None

    @staticmethod
    def _check_search_similarity(track_data, title, artist, threshold=0.5):
        """
        Check if the track is compatible with the title and artist using a similarity score.

        Args:
            track (dict): The track data parsed from the platform.
            title (str): The title to compare.
            artist (str): The artist to compare.
            threshold (float): The minimum similarity score (between 0 and 1) to consider a match.

        Returns:
            bool: True if the track is compatible, False otherwise.
        """
        # TODO : améliorer la similarité ??
        title_similarity = SequenceMatcher(None, track_data["title"].lower(), title.lower()).ratio()
        artist_similarity = SequenceMatcher(None, track_data["artist"].lower(), artist.lower()).ratio()
        print("title_similarity", title_similarity)
        print("artist_similarity", artist_similarity)
        return title_similarity >= threshold and artist_similarity >= threshold

    @staticmethod
    def concat_query(title, artist):
        """
        Concatenate the title and artist
        """
        return f"{title} {artist}"

    @abstractmethod
    def get_auth_url(self):
        """
        Returns the authorization url for the client
        """
        pass

    @abstractmethod
    def authenticate_with_code(self, code):
        """
        Authenticates the client using an authorization code (callback of the auth url) and stores the token data.
        - If the code is invalid it will raise an error
        - Set the token data in self.token_data
        - Set the client in self.client

        Parameters
        code: The authorization code
        """
        # TODO : ajouter raise si le code n'est pas valide
        pass

    @abstractmethod
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
        # TODO : ajouter raise si le token n'est pas valide
        pass

    @abstractmethod
    def fetch_saved_tracks(self):
        """
        Use self.client to get the list of saved tracks

        Returns: Raw data of the saved tracks
        """
        pass

    @abstractmethod
    def fetch_search(self, query, limit):
        """
        Use self.client to search for a track

        Parameters
        query: The query to search for
        limit: The maximum number of results

        Returns: Raw data of the search
        """
        pass

    @abstractmethod
    def like_track(self, track_id):
        """
        Use self.client to like a track

        Returns
        bool: True if success, False otherwise
        """
        pass

    @abstractmethod
    def unlike_track(self, track_id):
        """
        Use self.client to unlike a track

        Returns
        bool: True if success, False otherwise
        """
        pass

    @abstractmethod
    def clear_saved_tracks(self):
        """
        Use self.client to clear saved tracks

        Returns
        bool: True if success, False otherwise
        """
        pass

    @property
    def token_data(self):
        """
        Returns the token data

        Returns a dictionary with the access token and other information

        Raises
        ValueError: If the client has not been authenticated
        """
        if self._token_data is None:
            raise ValueError("You need to authenticate the client first."
                             "Call authenticate_with_code(code) or authenticate_with_token_data(token_data) first.")
        return self._token_data

    @token_data.setter
    def token_data(self, token_data):
        """
        Sets the token data

        Parameters
        token_data: A dictionary with the access token and other information
           {"access_token": "your_access_token",
            "refresh_token": "your_refresh_token",
            "expires_at": "expires_at_datetime_aware",
            "scope": "your_scope"}
        """
        # TODO : ajouter vérification de la forme du dictionnaire et de la validité des informations
        # TODO : basculer ici la transformation de la date (naive vers aware ou timestamp vers aware)
        self._token_data = token_data

    @property
    def client(self):
        """
        Returns the client
        """
        if self._client is None:
            raise ValueError("You need to authenticate the client first."
                             "Call authenticate_with_code(code) or authenticate_with_token_data(token_data) first.")
        return self._client

    @client.setter
    def client(self, client):
        """
        Sets the client
        """
        self._client = client
