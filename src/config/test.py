from .base import *  # noqa

DATABASES["default"] = {  # noqa
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
