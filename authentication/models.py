import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models

TIMEZONES = [(tz, tz) for tz in pytz.all_timezones]


class Skill(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        ADMIN = "admin", "Admin"
        DEVELOPER = "developer", "Developer"
        SALES_MANAGER = "sales_manager", "Sales Manager"

    role = models.CharField(max_length=20, choices=Role.choices)
    skills = models.ManyToManyField(Skill, related_name="+", null=True, blank=True)
    time_zone = models.CharField(
        max_length=100,
        choices=TIMEZONES,
        null=True,
        blank=True,
    )
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.username
