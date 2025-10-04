from src.apps.accounts.serializers.accounts import (
    RegistrationStep1Serializer,
    RegistrationStep2Serializer,
)
from src.apps.accounts.services.accounts import user_service
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.db import transaction
from src.utils.functions import (
    check_field_confirmed,
    ensure_otp_cooldown,
    generate_random_string,
    get_otp_expire_time,
    send_confirm_email,
)


@extend_schema(tags=["auth"])
class RegistrationAPIView(ViewSet):
    """
    ViewSet for handling user registration.
    """

    authentication_classes = ()
    permission_classes = ()

    def get_serializer_class(self):
        """
        Return the serializer class for registration.
        """

        if self.action == "step1":
            return RegistrationStep1Serializer
        if self.action == "step2":
            return RegistrationStep2Serializer

    @transaction.atomic
    def step1(self, request, *args, **kwargs):
        """
        Handle user registration.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={
                "data": "Ссылка для подтверждения регистрации отправлена на вашу почту."
            },
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def step2(self, request, *args, **kwargs):
        """
        Handle the second step of user registration.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_service.confirm_user_url(
            serializer.validated_data.get("confirmation_url"),
            serializer.validated_data.get("email"),
        )
        return Response(
            data={"data": "Ваш адрес электронной почты успешно подтвержден"},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def resend_otp(self, request, *args, **kwargs):
        user = user_service.get(id=kwargs.get("id"))

        ensure_otp_cooldown(user)
        check_field_confirmed(user, "email_verified")

        user.otp = generate_random_string(14)
        user.otp_expire_time = get_otp_expire_time()

        send_confirm_email(user.otp, user.email)

        user.save()

        return Response(
            data={
                "data": "Повторная ссылка для подтверждения регистрации отправлена на вашу почту."
            },
            status=status.HTTP_200_OK,
        )
