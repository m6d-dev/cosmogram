import random
import string
from rest_framework import serializers
from typing import Dict, Union, Optional
from rest_framework import status
from datetime import datetime, timedelta
import pytz
from django.core.mail import send_mail
from smtplib import SMTPServerDisconnected
from django.db import models
from src.config.base import EMAIL_HOST_USER, EMAIL_TOKEN_EXPIRE_MINUTES, TIME_ZONE
from django.conf import settings

tz = pytz.timezone(TIME_ZONE)


def raise_validation_error(message: Union[str, Dict]) -> None:
    raise serializers.ValidationError(message)


def get_datetime() -> datetime:
    return datetime.now(tz).replace(tzinfo=None)


def raise_validation_error_detail(
    message: str, code: Optional[int] = status.HTTP_400_BAD_REQUEST
) -> None:
    raise serializers.ValidationError({"detail": message}, code=code)


def validate_string(value: str, error_message: str = None) -> None:
    error_message = error_message or "Строка не должна содержать специальные символы."
    if any(symbol in value for symbol in r"!@#$%^&*+=[]{}\|\\;:<>?"):
        raise_validation_error_detail(error_message)


def get_otp_expire_time():
    return get_datetime() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)


def generate_otp(min: int = 10000, max: int = 99999) -> int:
    return random.randint(min, max)


def generate_random_string(length: int = 8) -> str:
    """Generates a random string of specified length.

    Args:
        length (int, optional): Length of the generated string. Defaults to 8.

    Returns:
        str: Random string.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def send_confirm_email(confirmation_url, email):
    send_email_notification(
        "Подтверждения электронной почты",
        "Ссылка для подверждения:\n\n{}".format(
            confirmation_url,
        ),
        email,
    )


def send_email_notification(subject: str, message: str, recipients: list | str) -> None:
    from_email = EMAIL_HOST_USER
    recipient_list = [recipients] if isinstance(recipients, str) else recipients

    try:
        send_mail(subject, message, from_email, recipient_list)
    except (TimeoutError, SMTPServerDisconnected):
        raise_validation_error_detail(
            "Ошибка при отправке кода подтверждения. Попробуйте ещё раз"
        )


def get_expire_time_otp(model):
    if model.otp_expire_time is None:
        return get_datetime()
    return model.otp_expire_time.astimezone(tz).replace(tzinfo=None)


def confirm_instance_email(instance: models.Model) -> None:
    """
    Подтверждает адрес электронной почты модели.
    """
    instance.email_verified = True
    instance.otp = None
    instance.otp_expire_time = None
    instance.save()


def ensure_otp_cooldown(instance: models.Model) -> None:
    cooldown_time = timedelta(minutes=settings.CONFIRMATION_COLDOWN_MINUTES)
    last_otp_time = get_expire_time_otp(instance) - timedelta(
        minutes=EMAIL_TOKEN_EXPIRE_MINUTES
    )

    if last_otp_time + cooldown_time > get_datetime():
        raise_validation_error_detail(
            "Код подтверждения можно получать раз в %s минут."
            % settings.CONFIRMATION_COLDOWN_MINUTES
        )


def validate_otp_until_confirm(
    instance: models.Model,
    ver_code_field: str,
    ver_code: str,
    ver_code_expired_message: str = "Время действия секретного ключа истекло. Пожалуйста, запросите новый ключ.",
    invalid_ver_code_message: str = "Неверный код подтверждения",
) -> None:
    """
    Проверка валидности OTP-кода модели.
    """
    if getattr(instance, ver_code_field) != ver_code:
        raise_validation_error_detail(invalid_ver_code_message)
    if get_datetime() > get_expire_time_otp(instance):
        raise_validation_error_detail(ver_code_expired_message)


def check_field_confirmed(instance: models.Model, field: str) -> None:
    """
    Проверка поля на подтверждение.
    """
    if getattr(instance, field):
        raise_validation_error_detail("Уже подтверждено.")
