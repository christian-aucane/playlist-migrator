from pprint import pprint

from ..base.parser import BaseParser


class SpotifyParser(BaseParser):
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
