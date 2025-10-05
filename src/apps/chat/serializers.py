from rest_framework import serializers



class ChatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()
    is_read = serializers.BooleanField()
