import csv
from pathlib import Path

import xlrd
from django.db import transaction
from django.shortcuts import get_object_or_404
from openpyxl import load_workbook
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AnalysisService, Project, WaitlistLead
from .serializers import MappingSerializer, ProjectUploadSerializer, ServiceSerializer
from .tasks import run_analysis_task


def extract_headers(uploaded_file) -> list[str]:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".csv":
        uploaded_file.seek(0)
        line = uploaded_file.readline().decode("utf-8-sig")
        headers = next(csv.reader([line]))
    elif suffix == ".xlsx":
        uploaded_file.seek(0)
        workbook = load_workbook(uploaded_file, read_only=True, data_only=True)
        headers = next(workbook.active.iter_rows(values_only=True), ())
        workbook.close()
    else:
        uploaded_file.seek(0)
        workbook = xlrd.open_workbook(file_contents=uploaded_file.read(), on_demand=True)
        sheet = workbook.sheet_by_index(0)
        headers = sheet.row_values(0) if sheet.nrows else []
        workbook.release_resources()
    uploaded_file.seek(0)
    cleaned = [str(value).strip() for value in headers if value is not None and str(value).strip()]
    if not cleaned:
        raise ValueError("The uploaded file has no header row.")
    return cleaned


class ServiceListView(ListAPIView):
    queryset = AnalysisService.objects.all()
    serializer_class = ServiceSerializer


class ProjectUploadView(APIView):
    def post(self, request):
        serializer = ProjectUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            detected_columns = extract_headers(serializer.validated_data["file"])
        except (UnicodeDecodeError, csv.Error, ValueError, xlrd.XLRDError) as exc:
            return Response({"file": [str(exc)]}, status=status.HTTP_400_BAD_REQUEST)
        project = serializer.save(user=request.user)
        return Response({
            "project_id": str(project.id),
            "analysis_type": project.analysis_type,
            "detected_columns": detected_columns,
        }, status=status.HTTP_201_CREATED)


class OwnedProjectView(APIView):
    def get_project(self, project_id):
        return get_object_or_404(Project.objects.select_related("service"), pk=project_id, user=self.request.user)


class StartAnalysisView(OwnedProjectView):
    def post(self, request, project_id):
        project = self.get_project(project_id)
        if not project.service.is_active:
            return Response({"detail": "This service is available through the private beta waitlist."}, status=status.HTTP_409_CONFLICT)
        if project.status != Project.Status.PENDING:
            return Response({"detail": "This project has already been submitted."}, status=status.HTTP_409_CONFLICT)
        serializer = MappingSerializer(data=request.data, context={"project": project})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = type(request.user).objects.select_for_update().get(pk=request.user.pk)
            if user.credit_limit < 1:
                return Response({"detail": "No analysis credits remain."}, status=status.HTTP_402_PAYMENT_REQUIRED)
            user.credit_limit -= 1
            user.save(update_fields=("credit_limit",))
            project.data_mapping = serializer.validated_data["mapping"]
            project.status = Project.Status.PROCESSING
            project.save(update_fields=("data_mapping", "status"))
            transaction.on_commit(lambda: run_analysis_task.delay(str(project.id)))
        return Response({
            "project_id": str(project.id),
            "status": Project.Status.PROCESSING,
            "message": "Data ingestion complete. Analysis added to Celery queue.",
        }, status=status.HTTP_202_ACCEPTED)


class ProjectStatusView(OwnedProjectView):
    def get(self, request, project_id):
        project = self.get_project(project_id)
        response = {"status": project.status}
        if project.status == Project.Status.FAILED:
            response["error"] = project.error_log
        return Response(response)


class RFMResultView(OwnedProjectView):
    def get(self, request, project_id):
        result = self.get_project(project_id).rfm_result
        return Response({
            "summary": result.summary,
            "chart_data": result.chart_data,
            "actionable_insights": result.actionable_insights,
            "download_excel_url": result.result_file_path,
        })


class BasketResultView(OwnedProjectView):
    def get(self, request, project_id):
        return Response({"rules": self.get_project(project_id).basket_result.rules})


class PredictiveResultView(OwnedProjectView):
    def get(self, request, project_id):
        project = self.get_project(project_id)
        result = project.ml_result
        payload = {"analysis_type": project.analysis_type, "summary": result.metrics}
        payload["anomalies_list" if project.analysis_type == "ANOMALY" else "scores"] = result.visualization_data
        return Response(payload)


class JoinWaitlistView(OwnedProjectView):
    def post(self, request, project_id):
        project = self.get_project(project_id)
        WaitlistLead.objects.get_or_create(project=project, defaults={"user": request.user})
        return Response({
            "status": "waitlisted",
            "message": "Your request for this automated engine has been registered. Our accounts team will contact you shortly to run an isolated private-beta trial on your raw data.",
        })
