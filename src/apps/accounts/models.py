from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

from src.apps.accounts.managers import UserManager
from src.utils.bases.models import AbstractTimestampsModel


class User(AbstractBaseUser, AbstractTimestampsModel):
    display_name = models.CharField(max_length=20)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    otp = models.CharField(max_length=40, blank=True, null=True)

    otp_expire_time = models.DateTimeField(
        verbose_name="Время исчерпания otp",
        blank=True,
        null=True,
        help_text="Дата и время исчерпания otp",
    )

    is_active = models.BooleanField(default=False)

    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"
