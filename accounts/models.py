from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    institution = models.CharField(max_length=50, null=True, blank=False)
    phone_number = models.CharField(max_length=50, null=True, blank=False)
