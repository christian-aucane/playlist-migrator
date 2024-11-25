from django.contrib import admin

from .models import OAuthToken


@admin.register(OAuthToken)
# Register your models here.
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'access_token', 'expires_at', 'created_at', 'updated_at')
    list_filter = ('user', 'platform')
    search_fields = ('user', 'platform')
    readonly_fields = ('user', 'platform', 'access_token', 'refresh_token', 'expires_at', 'created_at', 'updated_at')
    fields = ('user', 'platform', 'access_token', 'refresh_token', 'expires_at', 'created_at', 'updated_at')