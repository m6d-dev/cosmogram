from django.db import models
from django.db.models import Index

from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel


class ScientificArticle(AbstractAuditableModel, AbstractTimestampsModel):
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()

    file = models.ForeignKey(
        "content.File",
        on_delete=models.CASCADE,
        related_name="articles",
        null=False,
        blank=False,
    )
    tags = models.ManyToManyField(
        "content.Tag",
        through="ScientificArticleTags",
        related_name="scientific_articles",
    )

    class Meta:
        ordering = ["title"]


class ScientificArticleTags(AbstractAuditableModel, AbstractTimestampsModel):
    tag = models.ForeignKey("content.Tag", on_delete=models.CASCADE)
    scientific_article = models.ForeignKey(
        "ScientificArticle", on_delete=models.CASCADE
    )

    updated_at = None
    updated_by = None

    class Meta:
        ordering = ["tag"]
        constraints = [
            models.UniqueConstraint(
                fields=["scientific_article", "tag"],
                name="uq_scientific_article_tag",
            ),
        ]
        indexes = [
            models.Index(fields=["scientific_article"]),
        ]


class ScientificArticleImage(AbstractAuditableModel, AbstractTimestampsModel):
    title = models.CharField(max_length=255, db_index=True)
    image = models.ForeignKey("content.Image", on_delete=models.CASCADE)
    scientific_article = models.ForeignKey(
        "ScientificArticle", on_delete=models.CASCADE
    )

    updated_at = None
    updated_by = None

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(
                fields=["scientific_article", "title"],
                name="uq_article_image_title",
            ),
        ]
        indexes = [
            models.Index(fields=["scientific_article"]),
        ]


class ScientificArticleLike(AbstractAuditableModel, AbstractTimestampsModel):
    like = models.ForeignKey(
        "content.Like",
        on_delete=models.CASCADE,
    )
    scientific_article = models.ForeignKey(
        "ScientificArticle",
        on_delete=models.CASCADE,
    )

    updated_at = None
    updated_by = None

    class Meta:
        ordering = ["like"]
        indexes = [Index(fields=["scientific_article"])]


class ScientificArticleComments(AbstractAuditableModel, AbstractTimestampsModel):
    comment = models.ForeignKey(
        "content.Comment",
        on_delete=models.CASCADE,
    )
    scientific_article = models.ForeignKey(
        "ScientificArticle",
        on_delete=models.CASCADE,
    )

    updated_at = None
    updated_by = None

    class Meta:
        ordering = ["comment"]
        indexes = [Index(fields=["scientific_article"])]
