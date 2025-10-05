from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

from .logging import LOGGING  # noqa

load_dotenv()


SECRET_KEY = "django-insecure-c(!p+^7xlmnao&i!o&eijk4tpa=f7d=w1n660+up4wa324g#p$"

DEBUG = True

ALLOWED_HOSTS = [
    "api.cosmogram.anbor.tj",
    "crm-ecommerce-backend-prod-api-1",
    "127.0.0.1",
    "localhost"
]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # libraries
    "channels",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "django_extensions",
    # apps
    "src.apps.accounts",
    "src.apps.content",
    "src.apps.scientific_article",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = "src.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "src.config.wsgi.application"

# ============== REST FRAMEWORK ==============
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "COMPONENT_SPLIT_REQUEST": True,
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
}

# ============== DATABASE ==============
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_INTERNAL_PORT"),
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE") or "UTC"

CONFIRMATION_COLDOWN_MINUTES = 1

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

APP_URL = "apps"
APP_ROOT = os.path.join(MEDIA_ROOT, APP_URL)


ASGI_APPLICATION = "src.config.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SPECTACULAR_SETTINGS = {
    "TITLE": "Cosmogram System API Documentation",
    "DESCRIPTION": "Private API Documentation",
    "VERSION": "v1.0.0-alpha",
}

AUTH_USER_MODEL = "accounts.User"

# ============== JWT ==============
SIMPLE_JWT = {
    "ALGORITHM": os.environ.get("ALGORITHM", "HS256"),
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("ACCESS_TOKEN_LIFETIME", 5))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.environ.get("REFRESH_TOKEN_LIFETIME", 1))
    ),
    "SLIDING_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("ACCESS_TOKEN_LIFETIME", 5))
    ),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(
        days=int(os.environ.get("REFRESH_TOKEN_LIFETIME", 1))
    ),
    "UPDATE_LAST_LOGIN": True,
}

CELERY_BROKER_URL = f"redis://{os.environ.get("MQ_HOST")}:{os.environ.get("MQ_PORT")}/0"
CELERY_RESULT_BACKEND = (
    f"redis://{os.environ.get("MQ_HOST")}:{os.environ.get("MQ_PORT")}/0"
)

BOOTSTRAP_KEY = os.getenv("BOOTSTRAP_KEY")


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "send.message.2333@gmail.com"
EMAIL_HOST_PASSWORD = "cxqtyzyyocggucmr"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 1
EMAIL_TOKEN_EXPIRE_MINUTES = 5
DEFAULT_FROM_EMAIL = "send.message.2333@gmail.com"
