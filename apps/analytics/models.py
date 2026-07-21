import uuid

from django.conf import settings
from django.db import models


class AnalysisService(models.Model):
    class ResultKind(models.TextChoices):
        RFM = "RFM", "RFM"
        BASKET = "BASKET", "Market basket"
        PREDICTIVE = "PREDICTIVE", "Predictive"

    code = models.CharField(max_length=20, unique=True)
    name_en = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    result_kind = models.CharField(max_length=15, choices=ResultKind.choices)
    required_mapping_fields = models.JSONField(default=list)
    optional_mapping_fields = models.JSONField(default=list, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "code")

    def __str__(self) -> str:
        return f"{self.code} - {self.name_en}"


class Project(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        WAITLISTED = "WAITLISTED", "Private beta requested"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    service = models.ForeignKey(AnalysisService, on_delete=models.PROTECT, related_name="projects")
    analysis_type = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    raw_file_path = models.FileField(upload_to="uploads/")
    data_mapping = models.JSONField(default=dict)
    error_log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("user", "status"))]

    def save(self, *args, **kwargs):
        self.analysis_type = self.service.code
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.analysis_type})"


class RFMResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, related_name="rfm_result")
    summary = models.JSONField(default=dict)
    chart_data = models.JSONField(default=list)
    actionable_insights = models.JSONField(default=list)
    result_file_path = models.CharField(max_length=255, blank=True)


class BasketResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, related_name="basket_result")
    rules = models.JSONField(default=list)


class MLResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, related_name="ml_result")
    metrics = models.JSONField(default=dict)
    visualization_data = models.JSONField(default=list)


class WaitlistLead(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="waitlist_lead")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="waitlist_leads")
    created_at = models.DateTimeField(auto_now_add=True)
    contacted_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user} - {self.project.analysis_type}"
