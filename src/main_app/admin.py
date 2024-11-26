from django.contrib import admin

from .models import Track, TrackPlatformInfo, UserTrack


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'duration_ms', 'created_at', 'updated_at')
    search_fields = ('title', 'artist', 'album')
    list_filter = ('artist', 'created_at')


@admin.register(TrackPlatformInfo)
class TrackPlatformInfoAdmin(admin.ModelAdmin):
    list_display = ('track', 'platform', 'platform_id', 'url', 'created_at', 'updated_at')
    search_fields = ('platform', 'platform_id')
    list_filter = ('platform', 'created_at')


@admin.register(UserTrack)
class UserTrackAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'from_platform', 'created_at', 'updated_at')
    search_fields = ('user', 'track', 'from_platform')
    list_filter = ('from_platform', 'created_at')
