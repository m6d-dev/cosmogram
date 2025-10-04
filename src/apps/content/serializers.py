from rest_framework import serializers
from src.apps.content.services.post import post_service
from src.apps.content.models.post import Post


class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        write_only=True
    )
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    images_urls = serializers.SerializerMethodField(read_only=True)

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
        )

    def create(self, validated_data):
        instance = post_service.create(**validated_data)
        return instance
class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

class ListPostSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()
    images = ImageSerializer(many=True)