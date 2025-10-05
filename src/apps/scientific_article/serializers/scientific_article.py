from urllib.parse import urlsplit

from django.db import transaction
from django.utils.text import Truncator
from rest_framework import serializers

from src.apps.content.models import File, Tag, Image
from src.apps.scientific_article.models import (
    ScientificArticle,
    ScientificArticleTags,
    ScientificArticleImage,
)
from src.apps.scientific_article.models.scientific_article import (
    Author,
    ScientificArticleAuthors,
    ScientificArticleLike,
    ScientificArticleComments,
)
from src.utils.functions import raise_validation_error_detail


class UserShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    avatar = serializers.ImageField()
    username = serializers.CharField()


class ScientificArticleCommentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(required=True)
    created_by = UserShortSerializer()


class ScientificArticleImageSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=90)
    image = serializers.ImageField()

    def create(self, validated_data):
        raise NotImplementedError("Use parent serializer to create images.")


class ScientificArticleTagsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=60, required=False)  # имя тега

    def create(self, validated_data):
        raise NotImplementedError("Use parent serializer to create tags.")


class ScientificArticleFileSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=60)
    file = serializers.FileField()

    def create(self, validated_data):
        raise NotImplementedError("Use parent serializer to create file.")


class ScientificArticleCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False
    )
    file = ScientificArticleFileSerializer(required=True)
    images = ScientificArticleImageSerializer(many=True, required=True)
    authors = serializers.CharField(max_length=60, required=True)

    class Meta:
        model = ScientificArticle
        fields = ("title", "content", "authors", "tags", "images", "file")

    def is_valid(self, *, raise_exception=False):
        return super().is_valid(raise_exception=raise_exception)

    def _get_user(self):
        return self.context["request"].user

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        authors_data = validated_data.pop("authors", [])
        file_data = validated_data.pop("file")
        images_data = validated_data.pop("images")

        content_file = File.objects.create(
            title=file_data["title"],
            file=file_data["file"],
        )

        article = ScientificArticle.objects.create(
            file=content_file,
            **validated_data,
        )

        if tags_data:
            through_rows = []
            for t in tags_data:
                t = t.strip()
                tag_obj, _ = Tag.objects.get_or_create(name=t)
                through_rows.append(
                    ScientificArticleTags(
                        scientific_article=article,
                        tag=tag_obj,
                    )
                )
            ScientificArticleTags.objects.bulk_create(
                through_rows, ignore_conflicts=True
            )
        if authors_data:
            through_rows = []
            for a in authors_data.strip().split(","):
                a = a.strip()
                if not a.strip():
                    continue
                author_obj, _ = Author.objects.get_or_create(
                    name=a, defaults={"created_by_id": self._get_user().id}
                )
                obj = ScientificArticleAuthors(
                    scientific_article=article,
                    author=author_obj
                )
                through_rows.append(obj)
            ScientificArticleAuthors.objects.bulk_create(
                through_rows, ignore_conflicts=True
            )

        img_links = []
        for im in images_data:
            uploaded = im["image"]
            title = (im.get("title") or "").strip()
            content_img = Image.objects.create(
                title=title,
                file=uploaded,
            )
            img_links.append(
                ScientificArticleImage(
                    scientific_article=article,
                    image=content_img,
                    title=title,
                )
            )
        ScientificArticleImage.objects.bulk_create(img_links)

        return article

    def validate_authors(self, value: str) -> str:
        if not value.strip().split(","):
            raise serializers.ValidationError("At least one author is required")

        return value

    def validate_images(self, images):
        if not images:
            raise serializers.ValidationError("At leat one image is required.")
        titles = [i.get("title") for i in images if i.get("title")]
        if len(titles) != len(set(titles)):
            raise serializers.ValidationError("Images titles must be unique. ")
        return images


class RelativeURLMixin:
    @staticmethod
    def to_relative_path(url: str | None) -> str | None:
        """
        Делает '/media/...': отбрасывает схему/домен, оставляет path(+query).
        Если url пустой — вернёт None.
        """
        if not url:
            return None
        s = urlsplit(str(url))
        path = s.path or ""
        if s.query:
            path += f"?{s.query}"
        return path or None


class ScientificArticleListSerializer(serializers.ModelSerializer, RelativeURLMixin):
    tags = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()

    class Meta:
        model = ScientificArticle
        fields = (
            "id",
            "title",
            "content_preview",
            "tags",
            "cover_image",
            "file",
            "comments_count",
            "likes_count",
        )

    def get_content_preview(self, obj):
        text = obj.content or ""
        limit = int(self.context.get("preview_limit", 160))
        return Truncator(text).chars(limit)

    def get_tags(self, obj):
        return [t.title for t in obj.tags.all()]

    def _first_prefetched_image(self, obj):
        images = getattr(obj, "prefetched_images", None)
        if images is not None:
            return images[0] if images else None
        return obj.scientificarticleimage_set.select_related("image").first()

    def get_cover_image(self, obj):
        link = self._first_prefetched_image(obj)
        file_field = getattr(getattr(link, "image", None), "file", None)
        return self.to_relative_path(getattr(file_field, "url", None))

    def get_file(self, obj):
        file_field = getattr(getattr(obj, "file", None), "file", None)
        return self.to_relative_path(getattr(file_field, "url", None))


class ScientificArticleDetailSerializer(serializers.ModelSerializer, RelativeURLMixin):
    tags = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    comments = ScientificArticleCommentListSerializer(many=True, required=False)

    class Meta:
        model = ScientificArticle
        fields = (
            "id",
            "title",
            "content",
            "authors",
            "tags",
            "images",
            "file",
            "comments",
        )

    def get_tags(self, obj):
        return [t.title for t in obj.tags.all()]

    def get_authors(self, obj):
        return [a.name for a in obj.authors.all()]

    def get_images(self, obj):
        links = getattr(obj, "prefetched_images", None)
        if links is None:
            links = obj.scientificarticleimage_set.select_related("image").all()

        result = []
        for lee in links:
            file_field = getattr(getattr(lee, "image", None), "file", None)
            path = self.to_relative_path(getattr(file_field, "url", None))
            result.append(
                {
                    "title": getattr(lee, "title", "") or "",
                    "path": path,
                }
            )
        return result

    def get_file(self, obj):
        file_field = getattr(getattr(obj, "file", None), "file", None)
        return self.to_relative_path(getattr(file_field, "url", None))


class ScientificArticleLikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScientificArticleLike
        fields = ("scientific_article",)

    def _get_user(self):
        return self.context["request"].user

    def validate_scientific_article(self, obj: ScientificArticle):
        if obj.likes.filter(created_by=self._get_user()).exists():
            raise_validation_error_detail("Already liked.")
        return obj

    def create(self, validated_data):
        scientific_article = validated_data.pop("scientific_article")

        ScientificArticleLike.objects.create(
            created_by=self.context["request"].user,
            scientific_article=scientific_article,
        )

        scientific_article.likes_count += 1
        scientific_article.save(update_fields=["likes_count"])

        return scientific_article


class ScientificArticleCommentCreateSerializer(
    serializers.ModelSerializer, RelativeURLMixin
):
    class Meta:
        model = ScientificArticleComments
        fields = ("scientific_article", "content")

    def create(self, validated_data):
        scientific_article = validated_data.pop("scientific_article")
        ScientificArticleComments.objects.create(
            scientific_article=scientific_article,
            created_by=self.context["request"].user,
            **validated_data,
        )

        scientific_article.comments_count += 1
        scientific_article.save(update_fields=["comments_count"])

        return scientific_article
