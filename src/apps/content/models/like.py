from src.apps.content.models.post import Post
from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel
from django.db import models


class Like(AbstractAuditableModel, AbstractTimestampsModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )


class PostLike(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_likes",
    )
    like = models.ForeignKey(
        Like,
        on_delete=models.CASCADE,
        related_name="post_likes",
    )

    class Meta:
        unique_together = ("post", "like")
