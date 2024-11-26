from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from main_app.models import UserTrack
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

        return HttpResponseRedirect(reverse("main_app:index"))
