from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.base")

app = Celery("src.apps.celery")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
