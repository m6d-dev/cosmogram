from rest_framework import serializers
from src.apps.content.models.post import Post


class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "images",
        )

    def create(self, validated_data):

        instance = super().create(validated_data)
