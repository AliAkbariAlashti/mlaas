from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.authentication.models import User

from ..models import Project
from ..tasks import run_analysis_task


class MarketBasketFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+989120000001")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch("apps.analytics.views.run_analysis_task.delay")
    def test_upload_map_process_and_read_report(self, delay):
        upload = SimpleUploadedFile(
            "orders.csv",
            (
                "invoice,product,quantity\n"
                "1001,Coffee,1\n1001,Cake,1\n"
                "1002,Coffee,1\n1002,Cake,1\n"
                "1003,Coffee,1\n1003,Cake,1\n"
                "1004,Tea,1\n1004,Cake,1\n"
            ).encode(),
            content_type="text/csv",
        )
        uploaded = self.client.post(
            "/api/v1/projects/upload/",
            {"file": upload, "title": "Working basket report", "analysis_type": "MARKET_BASKET"},
            format="multipart",
        )
        self.assertEqual(uploaded.status_code, 201, uploaded.data)
        self.assertEqual(uploaded.data["detected_columns"], ["invoice", "product", "quantity"])

        project_id = uploaded.data["project_id"]
        with self.captureOnCommitCallbacks(execute=True):
            started = self.client.post(
                f"/api/v1/projects/{project_id}/start/",
                {"mapping": {
                    "invoice_id_column": "invoice",
                    "product_name_column": "product",
                    "quantity_column": "quantity",
                }},
                format="json",
            )
        self.assertEqual(started.status_code, 202, started.data)
        delay.assert_called_once_with(project_id)

        run_analysis_task.run(project_id)
        project = Project.objects.get(pk=project_id)
        self.assertEqual(project.status, Project.Status.SUCCESS)

        report = self.client.get(f"/api/v1/projects/{project_id}/basket-results/")
        self.assertEqual(report.status_code, 200, report.data)
        self.assertTrue(report.data["rules"])
        self.assertGreater(report.data["summary"]["rules_found"], 0)
        self.assertEqual(User.objects.get(pk=self.user.pk).credit_limit, 2)
