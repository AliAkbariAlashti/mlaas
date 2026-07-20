from rest_framework import serializers

from .models import BlogPost, ContactMessage


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = (
            "slug",
            "title_en",
            "title_fa",
            "excerpt_en",
            "excerpt_fa",
            "content_en",
            "content_fa",
            "published_at",
        )


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "phone_number", "company_name", "subject", "message")


class ContactResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
