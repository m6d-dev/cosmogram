from urllib.parse import urlsplit

from django.db import transaction
from django.utils.text import Truncator
from rest_framework import serializers

from src.apps.content.models import File, Tag, Image
from src.apps.scientific_article.models import ScientificArticle, ScientificArticleTags, ScientificArticleImage


class ScientificArticleImageSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=25)
    image = serializers.ImageField()

    def create(self, validated_data):
        raise NotImplementedError("Use parent serializer to create images.")


class ScientificArticleTagsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=25)  # имя тега

    def create(self, validated_data):
        raise NotImplementedError("Use parent serializer to create tags.")


class ScientificArticleFileSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=25)
    file = serializers.FileField()

    def create(self, validated_data):
        raise NotImplementedError("Use parent serializer to create file.")


class ScientificArticleCreateSerializer(serializers.ModelSerializer):
    tags = ScientificArticleTagsSerializer(many=True, required=False)
    file = ScientificArticleFileSerializer(required=True)
    images = ScientificArticleImageSerializer(many=True, required=True)

    class Meta:
        model = ScientificArticle
        fields = ("title", "content", "tags", "images", "file")

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
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
                tag_obj, _ = Tag.objects.get_or_create(title=t["title"])
                through_rows.append(
                    ScientificArticleTags(
                        scientific_article=article,
                        tag=tag_obj,
                    )
                )
            ScientificArticleTags.objects.bulk_create(through_rows, ignore_conflicts=True)

        img_links = []
        for im in images_data:
            uploaded = im["image"]
            title = im.get("title") or ""
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

    def validate_images(self, images):
        if not images:
            raise serializers.ValidationError("Нужна хотя бы одна картинка.")
        titles = [i.get("title") for i in images if i.get("title")]
        if len(titles) != len(set(titles)):
            raise serializers.ValidationError("Дублируются названия изображений внутри запроса.")
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

    class Meta:
        model = ScientificArticle
        fields = (
            "id",
            "title",
            "content",
            "tags",
            "images",
            "file",
        )

    def get_tags(self, obj):
        return [t.title for t in obj.tags.all()]

    def get_images(self, obj):
        links = getattr(obj, "prefetched_images", None)
        if links is None:
            links = obj.scientificarticleimage_set.select_related("image").all()

        result = []
        for l in links:
            file_field = getattr(getattr(l, "image", None), "file", None)
            path = self.to_relative_path(getattr(file_field, "url", None))
            result.append({
                "title": getattr(l, "title", "") or "",
                "path": path,
            })
        return result

    def get_file(self, obj):
        file_field = getattr(getattr(obj, "file", None), "file", None)
        return self.to_relative_path(getattr(file_field, "url", None))
