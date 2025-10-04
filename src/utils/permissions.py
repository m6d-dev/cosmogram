from django.http import HttpRequest
from django.views import View
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsUserActive(BasePermission):
    def has_permission(self, request: HttpRequest, view: View) -> bool:
        if request.user.is_active:  # type: ignore
            return True
        raise PermissionDenied("Ваш аккаунт не активен.")
