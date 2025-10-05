from src.apps.accounts.repositories.accounts import UserRepository, user_repo
from src.utils.bases.services import AbstractService
from src.apps.accounts.models import User
from rest_framework import serializers
from src.utils.functions import (
    confirm_instance_email,
    generate_otp,
    get_otp_expire_time,
    raise_validation_error_detail,
    validate_otp_until_confirm,
    send_confirm_email,
)
from typing import Union


class UserService(AbstractService[User]):
    def __init__(self, repository: UserRepository = user_repo):
        super().__init__(repository)

    def create(self, **kwargs) -> User:
        kwargs["otp"] = generate_otp()
        kwargs["otp_expire_time"] = get_otp_expire_time()
        password = kwargs.pop("password", None)
        user = self.model(**kwargs)
        if password:
            user.set_password(password)
        user.save()
        self._send_confirm_email(user=user)
        return user

    def confirm_user_url(
        self, confirmation_url: str, email: str
    ) -> Union[serializers.ValidationError, None]:
        user = user_service.get(email=email, otp=confirmation_url)

        if user is None:
            raise_validation_error_detail("Invalid otp code.")
        validate_otp_until_confirm(user, "otp", user.otp)

        confirm_instance_email(user)
        user.is_active = True
        user.save()

    def _send_confirm_email(self, user: User) -> None:
        send_confirm_email(confirmation_url=user.otp, email=user.email)


user_service = UserService()
