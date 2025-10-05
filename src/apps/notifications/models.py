from src.apps.accounts.models import User
from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel
from django.db import models


class Notification(AbstractAuditableModel, AbstractTimestampsModel):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    content = models.SlugField(max_length=100)
    type = models.SmallIntegerField()
    is_read = models.BooleanField(default=False, db_default=False)
