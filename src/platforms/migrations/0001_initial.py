# Generated by Django 5.1.3 on 2024-11-26 15:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPlatformAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('youtube', 'youtube'), ('spotify', 'spotify')], max_length=255)),
                ('action', models.CharField(max_length=255)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Platform Action',
                'verbose_name_plural': 'User Platform Actions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OAuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('youtube', 'youtube'), ('spotify', 'spotify')], help_text="The platform the token belongs to (e.g., 'youtube', 'spotify').", max_length=50)),
                ('access_token', models.TextField(help_text='The access token provided by the platform.')),
                ('refresh_token', models.TextField(blank=True, help_text='The refresh token provided by the platform.', null=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='The expiration time of the access token.', null=True)),
                ('scope', models.TextField(blank=True, help_text='The scopes associated with the token.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='The user who owns this token.', on_delete=django.db.models.deletion.CASCADE, related_name='oauth_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'OAuth Token',
                'verbose_name_plural': 'OAuth Tokens',
                'ordering': ['platform'],
                'unique_together': {('user', 'platform')},
            },
        ),
    ]
