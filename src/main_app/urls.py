from django.urls import path

from .views import AppIndexView, UpdateSavedTracksView

app_name = "main_app"

urlpatterns = [
    path("index/", AppIndexView.as_view(), name="index"),
    path("update_saved_tracks/<str:platform>/", UpdateSavedTracksView.as_view(), name="update_saved_tracks"),
]
