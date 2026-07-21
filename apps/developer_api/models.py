import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.analytics.models import AnalysisService


class APIEndpointPolicy(models.Model):
    name = models.CharField(max_length=100)
    path_prefix = models.CharField(max_length=255, unique=True)
    allow_api_keys = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("path_prefix",)
        verbose_name_plural = "API endpoint policies"

    def __str__(self):
        return self.name


class APIPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    monthly_request_limit = models.PositiveIntegerField(default=1_000)
    services = models.ManyToManyField(AnalysisService, blank=True, related_name="api_plans")
    endpoint_policies = models.ManyToManyField(
        APIEndpointPolicy, blank=True, related_name="plans"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class APISubscription(models.Model):
    class Status(models.TextChoices):
        TRIAL = "TRIAL", "Trial"
        ACTIVE = "ACTIVE", "Active"
        PAST_DUE = "PAST_DUE", "Past due"
        CANCELED = "CANCELED", "Canceled"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_subscription"
    )
    plan = models.ForeignKey(APIPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.TRIAL)
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_available(self):
        return self.status in {self.Status.TRIAL, self.Status.ACTIVE} and (
            not self.current_period_end or self.current_period_end >= timezone.now()
        )


class APIKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys"
    )
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=18, db_index=True)
    secret_hash = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    @classmethod
    def issue(cls, user, name):
        secret = f"mlaas_live_{secrets.token_urlsafe(32)}"
        api_key = cls.objects.create(
            user=user,
            name=name,
            prefix=secret[:18],
            secret_hash=hashlib.sha256(secret.encode()).hexdigest(),
        )
        return api_key, secret

    @classmethod
    def authenticate(cls, secret):
        if not secret or not secret.startswith("mlaas_live_"):
            return None
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        key = cls.objects.select_related(
            "user", "user__api_subscription", "user__api_subscription__plan"
        ).filter(secret_hash=secret_hash, is_active=True).first()
        if not key or not key.user.is_active:
            return None
        if key.expires_at and key.expires_at < timezone.now():
            return None
        return key

    def __str__(self):
        return f"{self.user} · {self.name}"


class APIUsage(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name="usage")
    endpoint_policy = models.ForeignKey(APIEndpointPolicy, on_delete=models.PROTECT)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    status_code = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("api_key", "created_at"))]


class DocumentationSection(models.Model):
    title_en = models.CharField(max_length=120)
    title_fa = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("display_order", "id")

    def __str__(self):
        return self.title_en


class DocumentationPage(models.Model):
    section = models.ForeignKey(
        DocumentationSection, on_delete=models.CASCADE, related_name="pages"
    )
    service = models.ForeignKey(
        AnalysisService,
        on_delete=models.SET_NULL,
        related_name="documentation_pages",
        null=True,
        blank=True,
    )
    title_en = models.CharField(max_length=180)
    title_fa = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    summary_en = models.TextField(blank=True)
    summary_fa = models.TextField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "id")

    def __str__(self):
        return self.title_en


class DocumentationBlock(models.Model):
    class Kind(models.TextChoices):
        TEXT = "TEXT", "Text"
        STEPS = "STEPS", "Numbered steps"
        CODE = "CODE", "Code example"
        SCHEMA = "SCHEMA", "CSV schema"
        REPORT = "REPORT", "Report explanation"
        CALLOUT = "CALLOUT", "Callout"

    page = models.ForeignKey(
        DocumentationPage, on_delete=models.CASCADE, related_name="blocks"
    )
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.TEXT)
    heading_en = models.CharField(max_length=180, blank=True)
    heading_fa = models.CharField(max_length=180, blank=True)
    content_en = models.TextField(blank=True)
    content_fa = models.TextField(blank=True)
    code = models.TextField(blank=True)
    code_language = models.CharField(max_length=30, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("display_order", "id")

    def __str__(self):
        return self.heading_en or f"{self.get_kind_display()} block"
