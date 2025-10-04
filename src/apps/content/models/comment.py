from django.db import models
from src.apps.content.models.post import Post
from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel


class Comment(AbstractAuditableModel, AbstractTimestampsModel):
    content = models.TextField(verbose_name="Контент")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )


class PostComment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_comments",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="post_comments",
    )

    class Meta:
        unique_together = ("post", "comment")
