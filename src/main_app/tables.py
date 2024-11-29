import django_tables2 as tables
from django.utils.safestring import mark_safe

from main_app.models import UserTrack


class UserTrackTable(tables.Table):
    title = tables.Column(accessor="track.title", verbose_name="Title")
    artist = tables.Column(accessor="track.artist", verbose_name="Artist")
    album = tables.Column(accessor="track.album", verbose_name="Album")
    duration = tables.Column(
        accessor="track.duration_ms",
        verbose_name="Duration",
        orderable=False
    )
    from_platform = tables.Column(verbose_name="Platform")
    added_at = tables.DateColumn(
        accessor="created_at",
        verbose_name="Added On",
        format="d/m/Y"
    )

    # TODO : ajouter des colonnes pour les plateformes dynamiquement avec settings.AVAILABLE_PLATFORMS
    spotify = tables.Column(verbose_name="Spotify", orderable=False, empty_values=())
    youtube = tables.Column(verbose_name="Youtube", orderable=False, empty_values=())

    delete = tables.Column(verbose_name="Delete", orderable=False, empty_values=())

    def render_duration(self, record):
        duration_ms = record.track.duration_ms
        duration_s = duration_ms / 1000
        return f"{duration_s / 60:.0f}:{duration_s % 60:02.0f}"

    def render_spotify(self, record):
        return self._render_platform_column(platform="spotify", record=record)

    def render_youtube(self, record):
        return self._render_platform_column(platform="youtube", record=record)

    def render_delete(self, record):
        # TODO : inclure directement le formulaire de suppression
        return mark_safe(f"<a href='{record.get_delete_url()}'>Delete</a>")

    @staticmethod
    def _render_platform_column(platform, record):
        """
        Dynamically adds a render method for the given platform.
        """
        track = record.track
        if track.is_avaiable_on_platform(platform=platform):
            url = track.platform_infos.get(platform=platform).url
            # TODO : transformer en lecteur dynamique ?
            return mark_safe(f"<a target='_blank' href='{url}'>Link</a>") if url else "dispo"
        return "pas dispo"

    class Meta:
        model = UserTrack
        template_name = "django_tables2/bootstrap5.html"
        fields = ("title", "artist", "album", "duration", "from_platform", "added_at", "spotify")
