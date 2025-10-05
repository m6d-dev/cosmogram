from rest_framework import serializers
from src.apps.accounts.serializers.accounts import UserSerializer
from src.apps.content.services.post import post_service
from src.apps.content.services.tag import tag_service
from src.apps.content.services.like import like_service
from src.apps.content.services.comment import comment_service
from src.apps.content.models.post import Post
from src.apps.content.models.comment import Comment
from src.utils.functions import raise_validation_error_detail


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
    created_by = UserSerializer()

    class Meta:
        model = Comment
        fields = ("id", "content", "created_by")


class ListPostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.SerializerMethodField()
    created_by = UserSerializer()
    created_at = serializers.DateTimeField()

    def get_likes(self, value):
        return value.likes.count()


class CreateLikeSerializer(serializers.Serializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post_id = serializers.IntegerField()

    def create(self, validated_data):
        return like_service.create(**validated_data)

    def validate(self, attrs):
        like_id = like_service.filter(
            post_id=attrs.get("post_id"), created_by_id=attrs.get("created_by").id
        ).values("id")
        if like_id:
            raise_validation_error_detail("You have already liked this post.")

        return attrs


class CommentSerializer(serializers.Serializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post_id = serializers.IntegerField()
    content = serializers.CharField()

    def create(self, validated_data):
        return comment_service.create(**validated_data)

    def validate_post_id(self, value):
        if not post_service.exists(id=value):
            raise_validation_error_detail("Post not found")
        return value
