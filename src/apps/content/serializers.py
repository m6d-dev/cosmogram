from rest_framework import serializers
from src.apps.content.services.post import post_service
from src.apps.content.services.tag import tag_service
from src.apps.content.models.post import Post
from src.apps.content.models.comment import Comment
from src.apps.content.models.like import Like


class TagField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        obj, created = tag_service.get_or_create(name=data)
        return obj


class TagSerializer(serializers.Serializer):
    name = serializers.CharField()


class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), required=True, write_only=True
    )
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    images_urls = serializers.SerializerMethodField(read_only=True)
    tags = TagField(slug_field="name", many=True, queryset=tag_service.all())

    def get_images_urls(self, obj):
        return [pi.image.image.url for pi in obj.post_images.all()]

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "images",
            "images_urls",
            "created_by",
            "tags",
        )

    def create(self, validated_data):
        instance = post_service.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        images = validated_data.pop("images")
        instance = super().update(instance=instance, validated_data=validated_data)
        post_service._set_images(instance=instance, images=images)
        return instance


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "content")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id",)


class ListPostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
