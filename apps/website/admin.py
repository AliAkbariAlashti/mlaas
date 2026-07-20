from django.contrib import admin

from .models import BlogPost, ContactMessage


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
