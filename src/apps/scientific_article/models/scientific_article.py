from django.db import models
from django.db.models import Index

from src.utils.bases.models import AbstractAuditableModel, AbstractTimestampsModel


class Author(AbstractAuditableModel, AbstractTimestampsModel):
    name = models.CharField(max_length=60, unique=True, db_index=True)

    updated_by = None
    updated_at = None


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
    authors = models.ManyToManyField(
        "Author",
        through="ScientificArticleAuthors",
    )
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["created_at"], name="idx_scient_article_created_at"),
        ]


class ScientificArticleAuthors(AbstractAuditableModel):
    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="scientific_articles",
        null=False,
        blank=False,
    )
    scientific_article = models.ForeignKey(
        "ScientificArticle",
        on_delete=models.CASCADE,
        db_index=True
    )



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
    scientific_article = models.ForeignKey(
        "ScientificArticle",
        on_delete=models.CASCADE,
        related_name="likes"
    )

    updated_at = None
    updated_by = None

    class Meta:
        indexes = [Index(fields=["scientific_article"])]


class ScientificArticleComments(AbstractAuditableModel, AbstractTimestampsModel):
    content = models.TextField()
    scientific_article = models.ForeignKey(
        "ScientificArticle",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    updated_at = None
    updated_by = None

    class Meta:
        ordering = ["scientific_article", "-created_at"]
        indexes = [Index(fields=["scientific_article", "created_at"])]
