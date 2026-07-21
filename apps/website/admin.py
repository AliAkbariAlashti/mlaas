from django.contrib import admin

from .models import BlogPost, ComponentPage, ContactMessage, HeaderMenuItem, ServicePage, ServiceStep


@admin.register(ComponentPage)
class ComponentPageAdmin(admin.ModelAdmin):
    list_display = ("title_en", "slug", "display_order")
    list_editable = ("display_order",)
    search_fields = ("title_en", "title_fa", "description_en", "description_fa")
    prepopulated_fields = {"slug": ("title_en",)}


@admin.register(HeaderMenuItem)
class HeaderMenuItemAdmin(admin.ModelAdmin):
    list_display = ("title_en", "parent", "component", "service", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("title_en", "title_fa")


class ServiceStepInline(admin.StackedInline):
    model = ServiceStep
    extra = 0


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    list_display = ("title_en", "service", "doc_id", "is_published")
    list_editable = ("is_published",)
    list_filter = ("is_published", "service__is_active")
    search_fields = ("title_en", "title_fa", "doc_id", "description_en", "description_fa")
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = (ServiceStepInline,)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title_en", "is_published", "published_at", "updated_at")
    list_editable = ("is_published",)
    list_filter = ("is_published", "published_at")
    search_fields = ("title_en", "title_fa", "content_en", "content_fa")
    prepopulated_fields = {"slug": ("title_en",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "subject", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone_number", "company_name", "subject", "message")
    readonly_fields = ("created_at",)
