from src.apps.accounts.serializers.accounts import (
    AvatarSetSerializer,
    RegistrationStep1Serializer,
    RegistrationStep2Serializer,
    UpdateProfileSerializer,
    UserMeSerializer,
)
from rest_framework.permissions import IsAuthenticated
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
    raise_validation_error_detail,
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
                "data": "The registration confirmation code has been sent to your email."
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
            serializer.validated_data.get("otp"),
            serializer.validated_data.get("email"),
        )
        return Response(
            data={"data": "Your email address has been successfully confirmed."},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def resend_otp(self, request, *args, **kwargs):
        user = user_service.get(id=kwargs.get("id"))

        ensure_otp_cooldown(user)
        check_field_confirmed(user, "confirmed")

        user.otp = generate_random_string(14)
        user.otp_expire_time = get_otp_expire_time()

        send_confirm_email(user.otp, user.email)

        user.save()

        return Response(
            data={
                "data": "A repeat code to confirm your registration has been sent to your email."
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["profile"])
class ProfileAPIView(ViewSet):

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "set_avatar":
            return AvatarSetSerializer
        if self.action == "profile_update":
            return UpdateProfileSerializer
        if self.action == "get_me":
            return UserMeSerializer

    @transaction.atomic
    def set_avatar(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer_class()(
            instance=instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_me(self, request, *args, **kwargs):
        instance = request.user
        if not instance:
            raise_validation_error_detail("Not found")

        serializer = self.get_serializer_class()(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def profile_update(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer_class()(
            instance=instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)
