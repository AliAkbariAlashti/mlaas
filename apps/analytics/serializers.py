from pathlib import Path

from rest_framework import serializers

from .models import AnalysisService, Project


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
        return Project.objects.create(service=service, analysis_type=service.code, **validated_data)


class MappingSerializer(serializers.Serializer):
    mapping = serializers.DictField(child=serializers.CharField(allow_null=True, allow_blank=False))

    def validate_mapping(self, mapping):
        project = self.context["project"]
        missing = [field for field in project.service.required_mapping_fields if not mapping.get(field)]
        if missing:
            raise serializers.ValidationError({"missing_required_fields": missing})
        return mapping
