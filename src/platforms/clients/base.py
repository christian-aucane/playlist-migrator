from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    Base class for all APIs clients
    """
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self._token_data = None

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
