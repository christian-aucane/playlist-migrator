from django.contrib import messages
from django.views.generic import TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django_tables2 import SingleTableView

from .models import UserTrack
from .services import MainAppService
from .tables import UserTrackTable


class AppIndexView(LoginRequiredMixin, TemplateView):
    template_name = "main_app/index.html"


class UpdateSavedTracksView(LoginRequiredMixin, View):
    def get(self, request, platform):
        app_service = MainAppService(user=request.user)
        success = app_service.update_user_tracks(platform=platform)

        if success:
            messages.success(request, "Saved tracks updated successfully.")
        else:
            messages.error(request, "Failed to update saved tracks.")
        return HttpResponseRedirect(reverse("main_app:user_track_table"))


class UserTrackDeleteView(LoginRequiredMixin, DeleteView):
    model = UserTrack
    success_url = reverse_lazy("main_app:user_track_table")


class UserTrackClearView(LoginRequiredMixin, View):
    def get(self, request):
        UserTrack.objects.filter(user=request.user).delete()
        return HttpResponseRedirect(reverse("main_app:user_track_table"))


class UserTrackTableView(LoginRequiredMixin, SingleTableView):
    model = UserTrack
    table_class = UserTrackTable
    template_name = "main_app/tracks.html"

    def get_queryset(self):
        """
        Returns tracks related to the logged-in user.
        """
        return UserTrack.objects.filter(user=self.request.user).select_related("track")
