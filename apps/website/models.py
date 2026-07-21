from django.db import models

from apps.analytics.models import AnalysisService


class ComponentPage(models.Model):
    slug = models.SlugField(unique=True)
    title_en = models.CharField(max_length=120)
    title_fa = models.CharField(max_length=120)
    description_en = models.TextField()
    description_fa = models.TextField()
    hero_media_url = models.URLField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "title_en")

    def __str__(self):
        return self.title_en


class HeaderMenuItem(models.Model):
    title_en = models.CharField(max_length=100)
    title_fa = models.CharField(max_length=100)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="children")
    component = models.ForeignKey(ComponentPage, blank=True, null=True, on_delete=models.SET_NULL, related_name="menu_items")
    service = models.ForeignKey(AnalysisService, blank=True, null=True, on_delete=models.SET_NULL, related_name="menu_items")
    url = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("display_order", "title_en")

    def __str__(self):
        return self.title_en


class ServicePage(models.Model):
    service = models.OneToOneField(AnalysisService, on_delete=models.CASCADE, related_name="website_page")
    slug = models.SlugField(unique=True)
    doc_id = models.CharField(max_length=50, unique=True)
    title_en = models.CharField(max_length=180)
    title_fa = models.CharField(max_length=180)
    description_en = models.TextField()
    description_fa = models.TextField()
    image_url = models.URLField(blank=True)
    hero_title_en = models.CharField(max_length=180)
    hero_title_fa = models.CharField(max_length=180)
    hero_media_url = models.URLField(blank=True)
    get_started_title_en = models.CharField(max_length=180, default="Ready to get started?")
    get_started_title_fa = models.CharField(max_length=180, default="آماده شروع هستید؟")
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title_en


class ServiceStep(models.Model):
    page = models.ForeignKey(ServicePage, on_delete=models.CASCADE, related_name="steps")
    title_en = models.CharField(max_length=160)
    title_fa = models.CharField(max_length=160)
    description_en = models.TextField()
    description_fa = models.TextField()
    image_url = models.URLField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "id")


class BlogPost(models.Model):
    slug = models.SlugField(max_length=180, unique=True)
    title_en = models.CharField(max_length=180)
    title_fa = models.CharField(max_length=180)
    excerpt_en = models.TextField()
    excerpt_fa = models.TextField()
    content_en = models.TextField()
    content_fa = models.TextField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")

    def __str__(self):
        return self.title_en


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RESOLVED = "RESOLVED", "Resolved"

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}: {self.subject}"
