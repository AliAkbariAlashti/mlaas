from rest_framework import serializers

from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ("id", "name", "prefix", "is_active", "created_at", "last_used_at")
        read_only_fields = fields


class CreateAPIKeySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class APIKeyCreatedSerializer(APIKeySerializer):
    secret = serializers.CharField(read_only=True)

    class Meta(APIKeySerializer.Meta):
        fields = APIKeySerializer.Meta.fields + ("secret",)


class APIAccessSerializer(serializers.Serializer):
    plan = serializers.CharField()
    status = serializers.CharField()
    monthly_request_limit = serializers.IntegerField()
    requests_used = serializers.IntegerField()
    requests_remaining = serializers.IntegerField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField(allow_null=True)
    services = serializers.ListField(child=serializers.DictField())
    endpoints = serializers.ListField(child=serializers.DictField())
