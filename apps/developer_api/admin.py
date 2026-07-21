from django.contrib import admin

from .models import (
    APIEndpointPolicy,
    APIKey,
    APIPlan,
    APISubscription,
    APIUsage,
    DocumentationBlock,
    DocumentationPage,
    DocumentationSection,
)


@admin.register(APIEndpointPolicy)
class APIEndpointPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "path_prefix", "allow_api_keys", "is_active")
    list_editable = ("allow_api_keys", "is_active")
    search_fields = ("name", "path_prefix")


@admin.register(APIPlan)
class APIPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_request_limit", "is_active")
    list_editable = ("monthly_request_limit", "is_active")
    filter_horizontal = ("services", "endpoint_policies")


@admin.register(APISubscription)
class APISubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "current_period_end")
    list_filter = ("status", "plan")
    search_fields = ("user__phone_number", "user__company_name")


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "prefix", "is_active", "last_used_at")
    list_filter = ("is_active",)
    search_fields = ("name", "prefix", "user__phone_number")
    readonly_fields = ("prefix", "secret_hash", "created_at", "last_used_at")


@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ("api_key", "endpoint_policy", "method", "status_code", "created_at")
    list_filter = ("endpoint_policy", "status_code", "method")
    readonly_fields = ("api_key", "endpoint_policy", "method", "path", "status_code", "created_at")


class DocumentationBlockInline(admin.StackedInline):
    model = DocumentationBlock
    extra = 0
    fields = (
        "display_order", "kind", "heading_en", "heading_fa", "content_en",
        "content_fa", "code", "code_language", "is_active",
    )


@admin.register(DocumentationSection)
class DocumentationSectionAdmin(admin.ModelAdmin):
    list_display = ("title_en", "title_fa", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    prepopulated_fields = {"slug": ("title_en",)}
    search_fields = ("title_en", "title_fa")


@admin.register(DocumentationPage)
class DocumentationPageAdmin(admin.ModelAdmin):
    list_display = ("title_en", "section", "service", "display_order", "is_active", "updated_at")
    list_filter = ("section", "service", "is_active")
    list_editable = ("display_order", "is_active")
    prepopulated_fields = {"slug": ("title_en",)}
    search_fields = ("title_en", "title_fa", "summary_en", "summary_fa")
    inlines = (DocumentationBlockInline,)


@admin.register(DocumentationBlock)
class DocumentationBlockAdmin(admin.ModelAdmin):
    list_display = ("page", "kind", "heading_en", "display_order", "is_active")
    list_filter = ("kind", "is_active", "page__section")
    list_editable = ("display_order", "is_active")
    search_fields = ("heading_en", "heading_fa", "content_en", "content_fa", "code")
