from django.contrib import admin

from .models import APIEndpointPolicy, APIKey, APIPlan, APISubscription, APIUsage


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
