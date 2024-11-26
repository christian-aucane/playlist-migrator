from abc import ABC, abstractmethod


class AbstractParser(ABC):
    """
    Abstract class for all APIs parsers
    """

    @abstractmethod
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
        # TODO : vérifier le format de la sortie ??
        pass


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
        return self.parser.parse_saved_tracks(data)

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
