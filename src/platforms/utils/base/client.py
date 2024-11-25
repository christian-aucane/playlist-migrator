from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    Base class for all APIs clients
    """
    def __init__(self):
        self._token_data = None
        self._client = None

    @abstractmethod
    def get_auth_url(self):
        """
        Returns the authorization url for the client
        """
        pass

    @abstractmethod
    def authenticate_with_code(self, code):
        """
        Authenticates the client

        Parameters
        code: The authorization code
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
            raise ValueError("You need to authenticate the client first. Call authenticate_with_code().")
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
