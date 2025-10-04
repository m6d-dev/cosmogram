from httpx import request
from rest_framework import serializers
from src.apps.accounts.services.accounts import user_service
from src.utils.functions import (
    raise_validation_error_detail,
    validate_string,
)
from django.core import validators
from django.db import transaction


class RegistrationStep1Serializer(serializers.Serializer):
    """
    Serializer for handling user registration data.
    """

    email = serializers.EmailField(required=True)
    display_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        self._validate_username_first_character(attrs.get("username"))
        self._validate_email(attrs.get("email"))
        validate_string(attrs.get("username"))
        self._validate_username_ascii(attrs.get("username"))
        return attrs

    def _validate_email(self, value):
        """
        Validate that the email is not already in use.
        """
        if user_service.filter(email=value).exists():
            raise_validation_error_detail("Данный email уже используется")
        validators.validate_email(value)
        return value

    def _validate_username_first_character(self, value):
        if not value[0].isalpha():
            raise_validation_error_detail("Никнейм должен начинаться с буквы")

    def _validate_username_ascii(self, value):
        if not value.isascii():
            raise_validation_error_detail("Никнейм не может содержать русские символы.")

    def validate_username(self, value):
        if user_service.exists(username=value):
            raise_validation_error_detail("Данный никнейм уже занят")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new user user with the validated data.
        """
        try:
            user = user_service.create(**validated_data)
        except Exception as e:
            raise_validation_error_detail(str(e))
        return validated_data


class RegistrationStep2Serializer(serializers.Serializer):
    otp = serializers.CharField()
    email = serializers.EmailField()


class UserMeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    confirmed = serializers.BooleanField()
    is_active = serializers.BooleanField()
    posts_count = serializers.IntegerField()
    display_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    subscription_count = serializers.IntegerField()
    subscribers_count = serializers.IntegerField()
