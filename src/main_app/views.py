from django.views.generic import TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django_tables2 import SingleTableView

from main_app.models import UserTrack
from main_app.tables import UserTrackTable
from platforms.service import PlatformService


class AppIndexView(LoginRequiredMixin, TemplateView):
    template_name = "main_app/index.html"


class UpdateSavedTracksView(LoginRequiredMixin, View):
    def get(self, request, platform):
        platform_service = PlatformService(platform=platform, user=request.user)

        saved_tracks = platform_service.fetch_saved_tracks()
        # TODO : créer un service qui sauvegarde les tracks, et vérifie si elles existent pour les autres plateformes
        for saved_track in saved_tracks:
            UserTrack.objects.add_user_track(
                user=request.user,
                track_data=saved_track,
                platform=platform
            )

        # TODO : ajouter gestion d'erreur

        return HttpResponseRedirect(reverse("main_app:tracks"))


class UserTrackDeleteView(LoginRequiredMixin, DeleteView):
    model = UserTrack
    success_url = reverse_lazy("main_app:user_track_table")

class UserTrackTableView(LoginRequiredMixin, SingleTableView):
    model = UserTrack
    table_class = UserTrackTable
    template_name = "main_app/tracks.html"

    def get_queryset(self):
        """
        Returns tracks related to the logged-in user.
        """
        return UserTrack.objects.filter(user=self.request.user).select_related("track")
