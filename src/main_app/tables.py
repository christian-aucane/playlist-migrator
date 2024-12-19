import django_tables2 as tables
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .models import UserTrack


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
        track = record.track
        if track.is_avaiable_on_platform(platform="spotify"):
            platform_id = track.platform_infos.get(platform="spotify").platform_id
            # TODO : Débugger iframe !!! ( erreurs dans le navigateur )
            return render_to_string("main_app/partials/spotify_embed.html", {"platform_id": platform_id})
        return "Pas dispo"

    def render_youtube(self, record):
        track = record.track
        if track.is_avaiable_on_platform(platform="youtube"):
            platform_id = track.platform_infos.get(platform="youtube").platform_id
            # TODO : débugger iframe !!! ( erreurs dans le navigateur )
            return render_to_string("main_app/partials/youtube_embed.html", {"platform_id": platform_id})
        return "Pas dispo"

    def render_delete(self, record):
        return mark_safe(f"<a href='{record.get_delete_url()}'>Delete</a>")

    class Meta:
        model = UserTrack
        template_name = "django_tables2/bootstrap5.html"
        fields = ("title", "artist", "album", "duration", "from_platform", "added_at", "spotify")
