from django.urls import path

from .views import AppIndexView, UpdateSavedTracksView, UserTrackTableView, UserTrackDeleteView

app_name = "main_app"

urlpatterns = [
    path("index/", AppIndexView.as_view(), name="index"),
    path("update_saved_tracks/<str:platform>/", UpdateSavedTracksView.as_view(), name="update_saved_tracks"),
    path("tracks/", UserTrackTableView.as_view(), name="user_track_table"),
    path("tracks/<int:pk>/delete/", UserTrackDeleteView.as_view(), name="user_track_delete"),
]
