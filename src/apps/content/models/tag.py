from django.db import models
from src.utils.bases.models import AbstractTimestampsModel


class Tag(AbstractTimestampsModel):
    name = models.CharField(max_length=50, unique=True)
