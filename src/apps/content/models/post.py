from src.apps.content.models.file import Image
from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel
from django.db import models


class Post(AbstractTimestampsModel, AbstractAuditableModel):
    updated_at = None

    title = models.CharField(verbose_name="Заголовок", max_length=100)
    content = models.TextField(verbose_name="Контент")
    images = models.ManyToManyField(
        Image, through="PostImage", related_name="posts", blank=True
    )

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="post_images",
    )
    image = models.ForeignKey(
        "Image",
        on_delete=models.CASCADE,
        related_name="image_posts",
    )

    class Meta:
        unique_together = ("post", "image")

    def __str__(self):
        return f"{self.post.title} - {self.image.image.name}"
