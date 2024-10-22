from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    institution = models.CharField(max_length=50, null=True, blank=False)
    Nomor_telpon = models.CharField(max_length=50, null=True, blank=False)
    nama_lengkap = models.CharField(max_length=500, null=True, blank=False)
    nik = models.CharField(max_length=50, null=False, blank=False)

