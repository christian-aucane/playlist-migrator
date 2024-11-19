from django.utils import timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .base import BaseClient


class YoutubeClient(BaseClient):
    def __init__(self, client_secrets_file, scopes, redirect_uri=None):
        super().__init__(scopes=scopes,
                         redirect_uri=redirect_uri)
        self.flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file,
            scopes,
            redirect_uri=redirect_uri
        )
        self.credentials = None
        self.youtube = None

    def get_auth_url(self):
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

        expires_at = None
        if self.credentials.expiry:
            expires_at = self.credentials.expiry  # datetime naive (without timezone information)

            # Convert to datetime aware (with timezone information)
            expires_at = timezone.make_aware(expires_at)

        self._token_data = {
            'access_token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'expires_at': expires_at,
            'scope': " ".join(self.credentials.scopes) if self.credentials.scopes else None,
        }

        # Instantiate the YouTube service client
        self.youtube = build("youtube", "v3", credentials=self.credentials)



if __name__ == "__main__":
    client = YoutubeClient(
        client_secrets_file="../../../client_secrets.json",
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
        redirect_uri="http://localhost:8080/callback"
    )

    print(client.get_auth_url())
