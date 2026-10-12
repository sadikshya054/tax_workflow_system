from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Defines the two main user roles in our system.
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        STAFF = 'STAFF', 'Staff'

    # Stores whether the account belongs to a client or staff member.
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
    )