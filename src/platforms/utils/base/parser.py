from abc import ABC, abstractmethod


class BaseParser(ABC):
    """
    Base class for all APIs parsers
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
