from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

from src.apps.accounts.views import RegistrationAPIView, ProfileAPIView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "register/",
        RegistrationAPIView.as_view({"post": "step1"}),
        name="step1_registration",
    ),
    path(
        "verify/",
        RegistrationAPIView.as_view({"post": "step2"}),
        name="step2_registration",
    ),
    path(
        "register/resend-otp/<int:id>/",
        RegistrationAPIView.as_view({"post": "resend_otp"}),
        name="resend_otp",
    ),
    path(
        "profiles/me/",
        ProfileAPIView.as_view({"get": "get_me"})
    ),
    path(
        "profile/update/",
        ProfileAPIView.as_view({"patch": "profile_update"})
    )
]
