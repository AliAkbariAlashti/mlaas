from pathlib import Path

from rest_framework import serializers

from .models import AnalysisService, Dataset, Project, RunEvent


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisService
        fields = ("code", "name_en", "name_fa", "is_active", "result_kind", "required_mapping_fields", "optional_mapping_fields")


class ProjectUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(max_length=100)
    analysis_type = serializers.CharField(max_length=20)

    def validate_file(self, value):
        if Path(value.name).suffix.lower() not in {".csv", ".xls", ".xlsx"}:
            raise serializers.ValidationError("Only CSV, XLS, and XLSX files are supported.")
        return value

    def validate_analysis_type(self, value):
        try:
            return AnalysisService.objects.get(code=value.upper())
        except AnalysisService.DoesNotExist as exc:
            raise serializers.ValidationError("Unknown analysis type.") from exc

    def create(self, validated_data):
        service = validated_data.pop("analysis_type")
        uploaded_file = validated_data.pop("file")
        dataset = Dataset.objects.create(
            user=validated_data["user"],
            name=validated_data["title"],
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_type=Path(uploaded_file.name).suffix.lower().lstrip("."),
            file_size=uploaded_file.size,
            detected_columns=self.context.get("detected_columns", []),
            validation_status=Dataset.ValidationStatus.VALID,
        )
        project = Project.objects.create(
            service=service,
            analysis_type=service.code,
            dataset=dataset,
            raw_file_path=dataset.file.name,
            **validated_data,
        )
        RunEvent.objects.create(run=project, stage=RunEvent.Stage.CREATED, message="Run created from uploaded dataset.")
        return project


class DatasetCreateSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=120)

    def validate_file(self, value):
        if Path(value.name).suffix.lower() not in {".csv", ".xls", ".xlsx"}:
            raise serializers.ValidationError("Only CSV, XLS, and XLSX files are supported.")
        return value


class DatasetSerializer(serializers.ModelSerializer):
    runs_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = (
            "id", "name", "original_filename", "file_type", "file_size", "row_count",
            "detected_columns", "validation_status", "validation_errors", "runs_count",
            "created_at", "updated_at", "last_used_at",
        )


class RunEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunEvent
        fields = ("id", "stage", "message", "metadata", "created_at")


class MappingSerializer(serializers.Serializer):
    mapping = serializers.DictField(child=serializers.CharField(allow_null=True, allow_blank=False))

    def validate_mapping(self, mapping):
        project = self.context["project"]
        missing = [field for field in project.service.required_mapping_fields if not mapping.get(field)]
        if missing:
            raise serializers.ValidationError({"missing_required_fields": missing})
        return mapping


class ProjectUploadResponseSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    analysis_type = serializers.CharField()
    detected_columns = serializers.ListField(child=serializers.CharField())


class StartAnalysisResponseSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    status = serializers.CharField()
    message = serializers.CharField()


class ProjectStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    error = serializers.CharField(required=False, allow_null=True)


class RFMResultSerializer(serializers.Serializer):
    summary = serializers.JSONField()
    chart_data = serializers.JSONField()
    actionable_insights = serializers.JSONField()
    download_excel_url = serializers.CharField()


class BasketResultSerializer(serializers.Serializer):
    summary = serializers.JSONField()
    rules = serializers.JSONField()


class PredictiveResultSerializer(serializers.Serializer):
    analysis_type = serializers.CharField()
    summary = serializers.JSONField()
    anomalies_list = serializers.JSONField(required=False)
    scores = serializers.JSONField(required=False)


class WaitlistResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()


class ProjectHistorySerializer(serializers.ModelSerializer):
    service_name_en = serializers.CharField(source="service.name_en", read_only=True)
    service_name_fa = serializers.CharField(source="service.name_fa", read_only=True)
    has_report = serializers.SerializerMethodField()
    dataset_name = serializers.CharField(source="dataset.name", read_only=True, allow_null=True)
    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "analysis_type",
            "service_name_en",
            "service_name_fa",
            "status",
            "dataset_name",
            "engine_version",
            "parameters",
            "started_at",
            "completed_at",
            "duration_seconds",
            "error_log",
            "has_report",
            "created_at",
        )

    def get_has_report(self, project) -> bool:
        relations = {
            AnalysisService.ResultKind.RFM: "rfm_result",
            AnalysisService.ResultKind.BASKET: "basket_result",
            AnalysisService.ResultKind.PREDICTIVE: "ml_result",
        }
        return hasattr(project, relations[project.service.result_kind])


class DashboardSerializer(serializers.Serializer):
    credits_remaining = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    successful_projects = serializers.IntegerField()
    processing_projects = serializers.IntegerField()
    failed_projects = serializers.IntegerField()
    waitlist_requests = serializers.IntegerField()
    recent_projects = ProjectHistorySerializer(many=True)
