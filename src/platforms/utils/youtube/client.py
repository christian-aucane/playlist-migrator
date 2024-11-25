from django.utils import timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from platforms.utils.base.client import BaseClient


class YoutubeClient(BaseClient):
    def __init__(self, client_secrets_file, scopes, redirect_uri=None):
        super().__init__()
        self.flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file,
            scopes,
            redirect_uri=redirect_uri
        )
        self.credentials = None

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
        self.credentials = self.flow.credentials

        self.token_data = {
            'access_token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'expires_at': timezone.make_aware(self.credentials.expiry) if self.credentials.expiry else None,  # datetime aware (with timezone
            # information)
            'scope': " ".join(self.credentials.scopes) if self.credentials.scopes else None,
        }

        # Instantiate the YouTube service client
        self._client = build("youtube", "v3", credentials=self.credentials)
