from django.contrib import admin

from .models import AnalysisService, BasketResult, Dataset, MLResult, Project, RFMResult, RunEvent, WaitlistLead


@admin.register(AnalysisService)
class AnalysisServiceAdmin(admin.ModelAdmin):
    list_display = ("code", "name_en", "is_active", "result_kind", "display_order")
    list_editable = ("is_active", "display_order")
    list_filter = ("is_active", "result_kind")
    search_fields = ("code", "name_en", "name_fa")
    ordering = ("display_order",)


class RFMResultInline(admin.StackedInline):
    model = RFMResult
    extra = 0


class BasketResultInline(admin.StackedInline):
    model = BasketResult
    extra = 0


class MLResultInline(admin.StackedInline):
    model = MLResult
    extra = 0


class RunEventInline(admin.TabularInline):
    model = RunEvent
    extra = 0
    readonly_fields = ("stage", "message", "metadata", "created_at")
    can_delete = False


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "analysis_type", "engine_version", "status", "created_at")
    list_filter = ("status", "service", "created_at")
    search_fields = ("title", "user__phone_number", "user__company_name")
    readonly_fields = ("id", "analysis_type", "created_at", "started_at", "completed_at")
    autocomplete_fields = ("user", "service", "dataset")
    date_hierarchy = "created_at"
    inlines = (RunEventInline, RFMResultInline, BasketResultInline, MLResultInline)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "file_type", "file_size", "validation_status", "created_at")
    list_filter = ("validation_status", "file_type", "created_at")
    search_fields = ("name", "original_filename", "user__phone_number", "user__company_name")
    readonly_fields = ("id", "file_size", "detected_columns", "created_at", "updated_at", "last_used_at")
    autocomplete_fields = ("user",)


@admin.register(WaitlistLead)
class WaitlistLeadAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "created_at", "contacted_at")
    list_filter = ("project__service", "created_at", "contacted_at")
    search_fields = ("user__phone_number", "user__company_name", "notes")
    autocomplete_fields = ("user", "project")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
