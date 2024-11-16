from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user template that extends Django's default user template.
    You can add fields specific to your application here if required.
    """

    def __str__(self):
        return self.username
