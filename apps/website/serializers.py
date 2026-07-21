from rest_framework import serializers

from .models import BlogPost, ComponentPage, ContactMessage, HeaderMenuItem, ServicePage, ServiceStep


class HeaderMenuItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()

    class Meta:
        model = HeaderMenuItem
        fields = ("id", "title_en", "title_fa", "href", "children")

    def get_children(self, item) -> list[dict]:
        return HeaderMenuItemSerializer(item.children.filter(is_active=True), many=True).data

    def get_href(self, item) -> str:
        if item.service and hasattr(item.service, "website_page"):
            return f"/services/{item.service.website_page.slug}"
        if item.component:
            return f"/components/{item.component.slug}"
        return item.url or "#"


class ComponentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentPage
        fields = ("slug", "title_en", "title_fa", "description_en", "description_fa", "hero_media_url")


class ServiceStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStep
        fields = ("title_en", "title_fa", "description_en", "description_fa", "image_url", "display_order")


class ServicePageSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="service.code", read_only=True)
    is_active = serializers.BooleanField(source="service.is_active", read_only=True)
    steps = ServiceStepSerializer(many=True, read_only=True)

    class Meta:
        model = ServicePage
        fields = ("slug", "code", "is_active", "doc_id", "title_en", "title_fa", "description_en", "description_fa", "image_url", "hero_title_en", "hero_title_fa", "hero_media_url", "get_started_title_en", "get_started_title_fa", "steps")


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
