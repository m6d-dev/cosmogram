from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField(max_length=150)
    created_at = serializers.DateTimeField()
    is_read = serializers.BooleanField()

    def save(self, **kwargs):
        return super().save(**kwargs)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
