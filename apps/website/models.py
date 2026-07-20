from django.db import models


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
