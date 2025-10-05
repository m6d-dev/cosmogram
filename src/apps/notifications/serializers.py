from rest_framework import serializers


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.SlugField()
    created_at = serializers.DateTimeField()
    is_read = serializers.BooleanField()
