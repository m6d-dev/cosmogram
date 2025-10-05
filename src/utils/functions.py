import random
import re
from typing import Any, List
from django.http import HttpRequest
import string
from rest_framework import serializers
from typing import Dict, Union
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


def validate_string(value: str, error_message: str = None) -> None:
    error_message = error_message or "Строка не должна содержать специальные символы."
    if any(symbol in value for symbol in r"!@#$%^&*+=[]{}\|\\;:<>?"):
        raise_validation_error_detail(error_message)


def raise_validation_error_detail(message: Union[str, Dict]) -> None:
    raise serializers.ValidationError(message)


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
        "Email confirmations",
        "Verification code:\n\n{}".format(
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
        raise_validation_error(
            "There was an error sending your verification code. Please try again."
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


def _get_first(data, key: str) -> Any:
    # data может быть QueryDict; берём одно значение (или None)
    if hasattr(data, "getlist"):
        lst = data.getlist(key)
        if lst:
            return lst[0]
    return data.get(key)


def _parse_tags(data) -> List[str]:
    """
    Принимаем:
      tags=AI  (повторяющиеся ключи)
      tags=AI&tags=ML
      tags[0]=AI&tags[1]=ML
    """
    tags: List[str] = []

    # 1) повторяющиеся tags
    if hasattr(data, "getlist"):
        for t in data.getlist("tags"):
            if t and t.strip():
                tags.append(t.strip())

    # 2) индексированные tags[i]
    rx_tag_idx = re.compile(r"^tags\[(\d+)\]$")
    indexed: Dict[int, str] = {}
    for k in data.keys():
        m = rx_tag_idx.match(k)
        if not m:
            continue
        idx = int(m.group(1))
        v = _get_first(data, k)
        if v and str(v).strip():
            indexed[idx] = str(v).strip()

    if indexed:
        for i in sorted(indexed.keys()):
            tags.append(indexed[i])

    return tags


def _parse_file(data) -> Dict[str, Any] | None:
    """
    Принимаем строго:
      file[title], file[file]
    """
    title = _get_first(data, "file[title]")
    blob = _get_first(data, "file[file]")  # это будет InMemoryUploadedFile внутри data

    if blob is None and title is None:
        return None

    # Пусть serializer валидирует обязательность. Здесь просто собираем.
    return {"title": title, "file": blob}


def _parse_indexed_objects(
    data, prefix: str, fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Для изображений:
      images[0][title], images[0][image]
      images[1][title], images[1][image]

    Возвращает список словарей с указанными полями, отсутствующие поля = None.
    """
    # паттерн: images[<idx>][<field>]
    rx = re.compile(rf"^{re.escape(prefix)}\[(\d+)\]\[(\w+)\]$")
    bag: Dict[int, Dict[str, Any]] = {}

    for k in data.keys():
        m = rx.match(k)
        if not m:
            continue
        idx = int(m.group(1))
        fld = m.group(2)
        if fld not in fields:
            continue
        bag.setdefault(idx, {})
        bag[idx][fld] = _get_first(data, k)

    # нормализуем: упорядочим по индексу и заполним отсутствующие поля None
    out: List[Dict[str, Any]] = []
    for i in sorted(bag.keys()):
        item = {f: bag[i].get(f) for f in fields}
        out.append(item)
    return out


def normalize_strict(request: HttpRequest) -> Dict[str, Any]:
    """
    Строго под ScientificArticleCreateSerializer:
      fields = ("title", "content", "authors", "tags", "images", "file")
    """
    data = request.data

    title = _get_first(data, "title")
    content = _get_first(data, "content")
    authors = _get_first(data, "authors")

    tags = _parse_tags(data)
    file_ = _parse_file(data)
    images = _parse_indexed_objects(data, prefix="images", fields=["title", "image"])

    return {
        "title": title,
        "content": content,
        "authors": authors,
        "tags": tags,
        "file": file_,
        "images": images,
    }
