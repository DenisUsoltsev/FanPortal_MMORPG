from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name="Аватарка")
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")
    token = models.CharField(max_length=15, blank=True, null=True)
